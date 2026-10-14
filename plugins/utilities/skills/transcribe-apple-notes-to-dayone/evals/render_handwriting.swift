// Render lines of text as a handwriting-style PNG, standing in for an Apple
// Notes drawing in eval fixtures. Used by build_fixtures.py; not part of the
// skill.
//
// Usage: swift render_handwriting.swift <out.png> <width> <height> <font-size> <line>...
// The height is computed from the line count when given as 0.
import AppKit

let args = CommandLine.arguments
guard args.count >= 6, let width = Int(args[2]), var height = Int(args[3]), let size = Double(args[4]) else {
    FileHandle.standardError.write("usage: swift render_handwriting.swift <out.png> <width> <height> <font-size> <line>...\n".data(using: .utf8)!)
    exit(1)
}
let lines = Array(args[5...])
let lineHeight = size * 1.7
let margin = size * 1.6
if height == 0 { height = Int(margin * 2 + lineHeight * Double(lines.count)) }

let font = NSFont(name: "Bradley Hand Bold", size: size) ?? NSFont.systemFont(ofSize: size)
let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: width, pixelsHigh: height, bitsPerSample: 8,
                           samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB,
                           bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
NSColor.white.setFill()
NSRect(x: 0, y: 0, width: width, height: height).fill()
let attributes: [NSAttributedString.Key: Any] = [.font: font, .foregroundColor: NSColor.black]
for (index, line) in lines.enumerated() {
    let y = Double(height) - margin - lineHeight * Double(index + 1)
    (line as NSString).draw(at: NSPoint(x: margin, y: y), withAttributes: attributes)
}
NSGraphicsContext.restoreGraphicsState()
try rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: args[1]))
