// Recognize handwriting in an image with Apple's Vision framework.
//
// Usage: swift ocr.swift <image> [<slice-dir>] [<max-slice-height>]
//
// Prints the recognized text, one line per detected line of handwriting.
// Images more than 10% taller than max-slice-height (default 2000 px) are
// cut into slices at fully blank rows, so no line of writing is split, and
// each slice is recognized separately; Vision misses or garbles much of a
// very tall image.
// When slice-dir is given, each slice is also saved there as sliceN.png so
// it can be compared against the text. Each slice's text is preceded by a
// "--- slice N" header.
import AppKit
import Foundation
import Vision

let args = CommandLine.arguments
guard args.count >= 2,
      let image = NSImage(contentsOf: URL(fileURLWithPath: args[1])),
      let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    FileHandle.standardError.write("usage: swift ocr.swift <image> [<slice-dir>] [<max-slice-height>]\n".data(using: .utf8)!)
    exit(1)
}
let sliceDir = args.count >= 3 ? args[2] : nil
let maxHeight = args.count >= 4 ? Int(args[3]) ?? 2000 : 2000

func recognize(_ image: CGImage) throws -> [String] {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    try VNImageRequestHandler(cgImage: image).perform([request])
    return (request.results ?? []).compactMap { $0.topCandidates(1).first?.string }
}

// A row is blank when every pixel is near white once drawn onto white.
func blankRows(_ image: CGImage) -> [Bool] {
    let width = image.width
    let height = image.height
    var pixels = [UInt8](repeating: 255, count: width * height * 4)
    let context = CGContext(data: &pixels, width: width, height: height, bitsPerComponent: 8,
                            bytesPerRow: width * 4, space: CGColorSpaceCreateDeviceRGB(),
                            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
    context.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
    context.fill(CGRect(x: 0, y: 0, width: width, height: height))
    context.draw(image, in: CGRect(x: 0, y: 0, width: width, height: height))
    return (0..<height).map { y in
        let row = y * width * 4
        for x in 0..<width where pixels[row + x * 4] < 200 || pixels[row + x * 4 + 1] < 200 || pixels[row + x * 4 + 2] < 200 {
            return false
        }
        return true
    }
}

func cuts(_ image: CGImage) -> [Int] {
    let height = image.height
    if height <= maxHeight { return [0, height] }
    let blank = blankRows(image)
    var result = [0]
    var y = 0
    // Leave at least minTail rows for the last slice; Vision rejects images
    // 2 px or less tall, and a sliver holds no writing anyway.
    let minTail = maxHeight / 10
    while height - y > maxHeight + minTail {
        let floor = y + maxHeight * 3 / 5
        var cut = y + maxHeight
        // Clamp the 6-row window: the first candidate can sit within 2 rows of the bottom.
        for t in stride(from: y + maxHeight, to: floor, by: -1)
        where (max(0, t - 3)..<min(height, t + 3)).allSatisfy({ blank[$0] }) {
            cut = t
            break
        }
        result.append(cut)
        y = cut
    }
    result.append(height)
    return result
}

let bounds = cuts(cg)
if let dir = sliceDir, bounds.count > 2 {
    try FileManager.default.createDirectory(atPath: dir, withIntermediateDirectories: true)
}
for i in 0..<(bounds.count - 1) {
    let rect = CGRect(x: 0, y: bounds[i], width: cg.width, height: bounds[i + 1] - bounds[i])
    guard let slice = cg.cropping(to: rect) else { continue }
    if bounds.count > 2 {
        print("--- slice \(i)")
        if let dir = sliceDir {
            let png = NSBitmapImageRep(cgImage: slice).representation(using: .png, properties: [:])!
            try png.write(to: URL(fileURLWithPath: "\(dir)/slice\(i).png"))
        }
    }
    for line in try recognize(slice) { print(line) }
}
