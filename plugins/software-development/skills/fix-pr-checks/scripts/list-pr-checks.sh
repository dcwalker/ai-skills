#!/bin/bash

# Script to list all status checks for a pull request
# Usage: ./list-pr-checks.sh [OPTIONS]
# Run with -h or --help for full usage information

# Auto-detect repository from git remote
REPO=$(git remote get-url origin 2>/dev/null | sed -E 's/.*github.com[:/]([^/]+)\/([^/]+)(\.git)?$/\1\/\2/' | sed 's/\.git$//')
if [ -z "$REPO" ]; then
  if [ -n "$GITHUB_REPOSITORY" ]; then
    REPO="$GITHUB_REPOSITORY"
  else
    echo "Error: Could not detect repository. Set GITHUB_REPOSITORY environment variable or run from a git repository."
    exit 1
  fi
fi

# Extract owner and repo name
OWNER=$(echo "$REPO" | cut -d'/' -f1)
REPO_NAME=$(echo "$REPO" | cut -d'/' -f2)

PULL_REQUEST=""
JOB_FILTER=""
SHOW_FAILING=""
SHOW_PASSING=""
SHOW_IN_PROGRESS=""
JSON_OUTPUT=""
COUNT_ONLY=""
HIDE_JOB_OUTPUT=""
FOLLOW=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -pr|--pull-request)
      PULL_REQUEST="$2"
      shift 2
      ;;
    -j|--job)
      JOB_FILTER="$2"
      shift 2
      ;;
    --show-failing)
      SHOW_FAILING="1"
      shift
      ;;
    --show-passing)
      SHOW_PASSING="1"
      shift
      ;;
    --show-in-progress)
      SHOW_IN_PROGRESS="1"
      shift
      ;;
    --json)
      JSON_OUTPUT="1"
      shift
      ;;
    --count)
      COUNT_ONLY="1"
      shift
      ;;
    --hide-job-output)
      HIDE_JOB_OUTPUT="1"
      shift
      ;;
    -f|--follow)
      FOLLOW="1"
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Description:"
      echo "  Lists all status checks for a pull request, including GitHub Actions"
      echo "  and other GitHub-native check runs and status contexts. Shows status,"
      echo "  duration, and annotations for failed checks. Supports follow mode for"
      echo "  real-time monitoring until all checks complete."
      echo ""
      echo "Options:"
      echo "  -pr, --pull-request <number>  Filter by pull request number (required)"
      echo "  -j, --job <name>              Filter by check/job name"
      echo "  --show-failing                 Filter to show only failing/errored checks (default: show all statuses)"
      echo "  --show-passing                 Filter to show only passing/successful checks (default: show all statuses)"
      echo "  --show-in-progress             Filter to show only in-progress/running checks (default: show all statuses)"
      echo "  --json                         Output only JSON (no formatted text)"
      echo "  --count                        Output only the count of items"
      echo "  --hide-job-output              Hide output for failed GitHub-native checks (e.g. CodeQL annotations)"
      echo "  -f, --follow                   Follow mode: show only summary and update every second until all checks complete"
      echo "  -h, --help                     Show this help message"
      echo ""
      echo "Note: By default, only checks from the most recent pipeline/run are shown (matching GitHub UI)."
      echo ""
      echo "Note: Status filters (--show-failing, --show-passing, --show-in-progress) can be combined."
      echo "      If multiple are specified, checks matching any of the specified statuses will be shown (OR logic)."
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use -h or --help for usage information"
      exit 1
      ;;
  esac
done

# Auto-detect PR number from current branch if not provided
if [ -z "$PULL_REQUEST" ]; then
  # Try to get PR number from current branch using gh CLI
  if command -v gh &> /dev/null && gh auth status &> /dev/null; then
    DETECTED_PR=$(gh pr view --json number 2>/dev/null | jq -r '.number // empty' 2>/dev/null)
    if [ -n "$DETECTED_PR" ] && [ "$DETECTED_PR" != "null" ] && [ "$DETECTED_PR" != "" ]; then
      PULL_REQUEST="$DETECTED_PR"
      if [ -z "$JSON_OUTPUT" ]; then
        echo "Auto-detected PR #${PULL_REQUEST} from current branch" >&2
      fi
    fi
  fi
fi

# Validate PR number is provided
if [ -z "$PULL_REQUEST" ]; then
  echo "Error: Pull request number is required. Use -pr or --pull-request to specify the PR number."
  echo "       Or run this script from a branch that has an associated pull request."
  echo "Use -h or --help for usage information"
  exit 1
fi

# Check if jq is available
if ! command -v jq &> /dev/null; then
  echo "Error: jq is not installed. Install it to use this script."
  exit 1
fi

# Check if curl is available
if ! command -v curl &> /dev/null; then
  echo "Error: curl is not installed. Install it to use this script."
  exit 1
fi

# Check if gh CLI is available (for GitHub API)
if ! command -v gh &> /dev/null; then
  echo "Error: GitHub CLI (gh) is not installed or not in PATH"
  echo "Install it from: https://cli.github.com/"
  exit 1
fi

# Check if gh is authenticated
if ! gh auth status &> /dev/null; then
  echo "Error: GitHub CLI is not authenticated."
  if [ -n "$GITHUB_TOKEN" ]; then
    echo ""
    echo "The GITHUB_TOKEN environment variable is set but appears to be invalid or expired."
    echo "To fix this, you can either:"
    echo "  1. Clear the invalid token: unset GITHUB_TOKEN"
    echo "  2. Set a valid token: export GITHUB_TOKEN=your_valid_token"
    echo "  3. Use GitHub CLI credentials: unset GITHUB_TOKEN && gh auth login"
  else
    echo "Run: gh auth login"
  fi
  exit 1
fi

# Function to get PR branch name from GitHub
get_pr_branch() {
  local pr_num="$1"
  
  local branch_info
  branch_info=$(gh api "repos/${REPO}/pulls/${pr_num}" 2>/dev/null | jq -r '.head.ref // empty' 2>/dev/null)
  if [ -n "$branch_info" ] && [ "$branch_info" != "null" ]; then
    echo "$branch_info"
    return 0
  fi
  
  return 1
}

# Function to get all status checks for a PR from GitHub
get_github_status_checks() {
  local pr_num="$1"
  
  # Get PR details to get the head SHA
  local pr_data
  pr_data=$(gh api "repos/${REPO}/pulls/${pr_num}" 2>/dev/null)
  if [ $? -ne 0 ] || [ -z "$pr_data" ]; then
    echo "[]"
    return 0
  fi
  
  local head_sha
  head_sha=$(echo "$pr_data" | jq -r '.head.sha // empty' 2>/dev/null)
  if [ -z "$head_sha" ] || [ "$head_sha" = "null" ]; then
    echo "[]"
    return 0
  fi
  
  # Get check runs for the commit (REST API - more reliable)
  # Use --paginate to get all pages of check runs
  local check_runs
  check_runs=$(gh api --paginate "repos/${REPO}/commits/${head_sha}/check-runs?per_page=100" 2>/dev/null)
  local check_runs_exit=$?
  
  # Get status contexts for the commit (REST API)
  # Note: Status endpoint is not paginated, returns all statuses in one response
  local statuses
  statuses=$(gh api "repos/${REPO}/commits/${head_sha}/status" 2>/dev/null)
  local statuses_exit=$?
  
  local all_checks="[]"
  
  # Process check runs
  # When using --paginate, gh api returns multiple JSON objects (one per page)
  # Each object has a .check_runs array, so we need to collect all of them
  if [ $check_runs_exit -eq 0 ] && [ -n "$check_runs" ]; then
    local runs
    # Collect all check_runs arrays from all pages and flatten into a single array
    runs=$(echo "$check_runs" | jq -s '[.[] | .check_runs[]?] | 
      map({
        name: .name,
        status: (if .status == "completed" then (.conclusion | ascii_downcase) else (.status | ascii_downcase) end),
        conclusion: (.conclusion // "" | ascii_downcase),
        description: (.output.summary // .app.name // "Unknown"),
        html_url: .html_url,
        started_at: .started_at,
        completed_at: .completed_at,
        context: .name,
        check_run_id: .id,
        is_codeql: ((.name | test("^CodeQL$"; "i")) or ((.app.name // "") | test("^CodeQL$"; "i"))),
        type: "check_run"
      })
    ' 2>/dev/null)
    
    if [ -n "$runs" ] && [ "$runs" != "null" ] && [ "$runs" != "[]" ]; then
      all_checks=$(echo "$all_checks" | jq --argjson runs "$runs" '. + $runs' 2>/dev/null || echo "$all_checks")
    fi
  fi
  
  # Process status contexts
  # Status endpoint returns a single object with a .statuses array
  if [ $statuses_exit -eq 0 ] && [ -n "$statuses" ]; then
    local contexts
    # Extract statuses array and map to our format
    contexts=$(echo "$statuses" | jq -r '
      .statuses[]? | {
        name: .context,
        status: (.state | ascii_downcase),
        conclusion: (.state | ascii_downcase),
        description: (.description // ""),
        html_url: .target_url,
        started_at: null,
        completed_at: null,
        context: .context,
        check_run_id: null,
        is_codeql: false,
        type: "status"
      }
    ' 2>/dev/null | jq -s '.' 2>/dev/null)
    
    if [ -n "$contexts" ] && [ "$contexts" != "null" ] && [ "$contexts" != "[]" ]; then
      all_checks=$(echo "$all_checks" | jq --argjson contexts "$contexts" '. + $contexts' 2>/dev/null || echo "$all_checks")
    fi
  fi
  
  # Remove duplicates (same context/name) - prefer check_runs over status contexts
  all_checks=$(echo "$all_checks" | jq '
    group_by(.context) |
    map(
      # If multiple entries for same context, prefer check_run over status
      (sort_by(.type == "status") | .[0])
    )
  ' 2>/dev/null || echo "$all_checks")
  
  
  if [ -z "$all_checks" ] || [ "$all_checks" = "null" ]; then
    echo "[]"
  else
    echo "$all_checks"
  fi
}

# Function to get check run annotations from GitHub API
get_check_run_annotations() {
  local check_run_id="$1"
  if [ -z "$check_run_id" ] || [ "$check_run_id" = "null" ] || [ "$check_run_id" = "" ]; then
    echo "[]"
    return 1
  fi
  
  # Fetch annotations with pagination support (--paginate handles all pages automatically)
  local annotations
  annotations=$(gh api --paginate "repos/${REPO}/check-runs/${check_run_id}/annotations?per_page=100" 2>/dev/null)
  local exit_code=$?
  
  if [ $exit_code -ne 0 ] || [ -z "$annotations" ]; then
    echo "[]"
    return 1
  fi
  
  # Check if it's a JSON array
  if ! echo "$annotations" | jq -e 'type == "array"' >/dev/null 2>&1; then
    echo "[]"
    return 1
  fi
  
  echo "$annotations"
}

# Function to fetch checks and display summary (for follow mode)
fetch_and_display_summary() {
  local is_update="$1"  # "1" if updating in-place, "0" if first display
  local is_first="$2"   # "true" if first iteration, "false" otherwise
  
  # Generate timestamp for when status was last refreshed
  local timestamp
  timestamp=$(date '+%b %d, %Y %H:%M:%S')
  
  # Get all status checks from GitHub (fetch data BEFORE clearing screen)
  local github_checks
  github_checks=$(get_github_status_checks "$PULL_REQUEST")
  
  # Ensure we have valid JSON
  if ! echo "$github_checks" | jq empty 2>/dev/null; then
    github_checks="[]"
  fi
  
  local check_count
  check_count=$(echo "$github_checks" | jq 'length // 0' 2>/dev/null || echo "0")
  
  # Ensure CHECK_COUNT is numeric
  if ! [[ "$check_count" =~ ^[0-9]+$ ]]; then
    check_count=0
  fi
  
  if [ "$check_count" -eq 0 ]; then
    if [ -z "$JSON_OUTPUT" ]; then
      if [ "$is_update" = "1" ]; then
        printf "\033[8A\033[0J"  # Clear previous output
      fi
      echo "No status checks found for PR #${PULL_REQUEST}"
    fi
    return 1
  fi
  
  local all_checks="$github_checks"

  # Apply filters
  local filtered_checks="$all_checks"

  # Apply job/check name filter
  if [ -n "$JOB_FILTER" ]; then
    filtered_checks=$(echo "$filtered_checks" | jq --arg filter "$JOB_FILTER" '[.[] | select(.name == $filter or .context == $filter or (.context | contains($filter)))]' 2>/dev/null || echo "$filtered_checks")
  fi

  # Apply status filters (OR logic - if multiple are specified, show checks matching any)
  # Map GitHub status values to our filter values
  if [ -n "$SHOW_FAILING" ] || [ -n "$SHOW_PASSING" ] || [ -n "$SHOW_IN_PROGRESS" ]; then
    local status_filter_parts=()
    
    if [ -n "$SHOW_FAILING" ]; then
      status_filter_parts+=("failed|error|failure")
    fi
    
    if [ -n "$SHOW_PASSING" ]; then
      status_filter_parts+=("success|successful")
    fi
    
    if [ -n "$SHOW_IN_PROGRESS" ]; then
      status_filter_parts+=("running|pending|in_progress|queued|in_progress|waiting")
    fi
    
    # Join all filter parts with |
    local status_filter
    status_filter=$(IFS='|'; echo "${status_filter_parts[*]}")
    
    # Filter checks by status (case-insensitive)
    filtered_checks=$(echo "$filtered_checks" | jq --arg filter "$status_filter" '
      [.[] | select(.status | ascii_downcase | test($filter; "i"))]
    ' 2>/dev/null || echo "$filtered_checks")
  fi
  
  # Calculate summary counts
  local failing_count
  failing_count=$(echo "$filtered_checks" | jq '[.[] | select(.status | ascii_downcase | test("failure|failed|error"; "i"))] | length' 2>/dev/null || echo "0")
  local expected_count
  expected_count=$(echo "$filtered_checks" | jq '[.[] | select((.type | ascii_downcase) == "expected")] | length' 2>/dev/null || echo "0")
  local pending_count
  pending_count=$(echo "$filtered_checks" | jq '[.[] | select((.status | ascii_downcase | test("pending|queued|waiting"; "i")) and ((.type | ascii_downcase) != "expected"))] | length' 2>/dev/null || echo "0")
  local success_count
  success_count=$(echo "$filtered_checks" | jq '[.[] | select(.status | ascii_downcase | test("success|successful"; "i"))] | length' 2>/dev/null || echo "0")
  local in_progress_count
  in_progress_count=$(echo "$filtered_checks" | jq '[.[] | select(.status | ascii_downcase | test("in_progress|running|inprogress"; "i"))] | length' 2>/dev/null || echo "0")
  local neutral_count
  neutral_count=$(echo "$filtered_checks" | jq '[.[] | select(.status | ascii_downcase | test("neutral|cancelled|canceled|skipped"; "i"))] | length' 2>/dev/null || echo "0")
  local unknown_count
  unknown_count=$(echo "$filtered_checks" | jq '[.[] | 
    (.type | ascii_downcase) as $type |
    (.status | ascii_downcase) as $status |
    select(
      ($type != "expected") and
      ($status | test("success|successful|failure|failed|error|pending|queued|waiting|in_progress|running|inprogress|neutral|cancelled|canceled|skipped"; "i") | not)
    )
  ] | length' 2>/dev/null || echo "0")
  
  # Ensure counts are numeric
  if ! [[ "$failing_count" =~ ^[0-9]+$ ]]; then
    failing_count=0
  fi
  if ! [[ "$expected_count" =~ ^[0-9]+$ ]]; then
    expected_count=0
  fi
  if ! [[ "$pending_count" =~ ^[0-9]+$ ]]; then
    pending_count=0
  fi
  if ! [[ "$success_count" =~ ^[0-9]+$ ]]; then
    success_count=0
  fi
  if ! [[ "$in_progress_count" =~ ^[0-9]+$ ]]; then
    in_progress_count=0
  fi
  if ! [[ "$neutral_count" =~ ^[0-9]+$ ]]; then
    neutral_count=0
  fi
  if ! [[ "$unknown_count" =~ ^[0-9]+$ ]]; then
    unknown_count=0
  fi
  
  # Build status key lines with only statuses that have counts > 0
  local status_key_lines=()
  if [ "$success_count" -gt 0 ]; then
    status_key_lines+=("🟢 Success ($success_count)")
  fi
  if [ "$in_progress_count" -gt 0 ] || [ "$expected_count" -gt 0 ]; then
    local total_in_progress=$((in_progress_count + expected_count))
    status_key_lines+=("🟠 In Progress/Expected ($total_in_progress)")
  fi
  if [ "$failing_count" -gt 0 ]; then
    status_key_lines+=("🔴 Failed ($failing_count)")
  fi
  if [ "$pending_count" -gt 0 ]; then
    status_key_lines+=("🟡 Pending ($pending_count)")
  fi
  if [ "$neutral_count" -gt 0 ]; then
    status_key_lines+=("⚪ Neutral/Cancelled ($neutral_count)")
  fi
  if [ "$unknown_count" -gt 0 ]; then
    status_key_lines+=("⚫ Unknown ($unknown_count)")
  fi
  
  # Get last commit SHA and summary from origin (via GitHub API) BEFORE clearing screen
  # Always fetch commit data for consistent line count
  local pr_data
  pr_data=$(gh api "repos/${REPO}/pulls/${PULL_REQUEST}" 2>/dev/null)
  local head_sha=""
  local short_sha=""
  local commit_summary=""
  
  if [ $? -eq 0 ] && [ -n "$pr_data" ]; then
    head_sha=$(echo "$pr_data" | jq -r '.head.sha // empty' 2>/dev/null)
    if [ -n "$head_sha" ] && [ "$head_sha" != "null" ] && [ "$head_sha" != "" ]; then
      # Get short SHA (first 7 characters)
      short_sha=$(echo "$head_sha" | cut -c1-7)
      
      # Get commit message summary (first line) from GitHub API
      local commit_data
      commit_data=$(gh api "repos/${REPO}/commits/${head_sha}" 2>/dev/null)
      if [ $? -eq 0 ] && [ -n "$commit_data" ]; then
        commit_summary=$(echo "$commit_data" | jq -r '.commit.message // ""' 2>/dev/null | head -n1 | sed 's/\r$//')
      fi
    fi
  fi
  
  # Build summary text BEFORE clearing screen - list each check with its status emoji
  local summary_lines
  summary_lines=$(echo "$filtered_checks" | jq -r '.[] | 
    (.type | ascii_downcase) as $type |
    (.status | ascii_downcase) as $status |
    (if $type == "expected" then "🟠"
     elif $status == "success" or $status == "successful" then "🟢"
     elif $status == "failure" or $status == "failed" or $status == "error" then "🔴"
     elif $status == "pending" or $status == "queued" or $status == "waiting" then "🟡"
     elif $status == "in_progress" or $status == "running" or $status == "inprogress" then "🟠"
     elif $status == "neutral" or $status == "cancelled" or $status == "canceled" or $status == "skipped" then "⚪"
     else "⚫" end) as $emoji |
    "\($emoji)  Check: \(.name // .context // "N/A")"
  ' 2>/dev/null)
  
  local summary_text=""
  if [ -n "$summary_lines" ] && [ "$summary_lines" != "" ]; then
    summary_text="$summary_lines"
  else
    summary_text="No checks found"
  fi
  
  # Now that we have ALL data ready (checks, counts, commit info), clear and display
  if [ "$is_update" = "1" ]; then
    # Restore cursor to saved position (start of our output area) and clear from there to end of screen
    printf "\033[u\033[0J"  # Restore cursor position and clear from cursor to end of screen
  elif [ "$is_first" = true ]; then
    # Save cursor position at start of output (after any initial messages)
    printf "\033[s"  # Save cursor position
  fi
  
  # Display summary (all data is now ready, print everything at once)
  # \033[2K clears the entire line (both before and after cursor)
  if [ "$is_update" = "1" ]; then
    # Print all lines at once, clearing each line first
    printf "\033[2K\rSummary:\n"
    # Print each check on its own line
    echo "$summary_text" | while IFS= read -r line || [ -n "$line" ]; do
      if [ -n "$line" ]; then
        printf "\033[2K\r%s\n" "$line"
      fi
    done
    # Print status key if there are any statuses to show
    if [ ${#status_key_lines[@]} -gt 0 ]; then
      printf "\033[2K\r\n"
      for key_line in "${status_key_lines[@]}"; do
        printf "\033[2K\r  %s\n" "$key_line"
      done
    fi
    printf "\033[2K\r\n"
    printf "\033[2K\rLast commit:\n"
    if [ -n "$short_sha" ] && [ "$short_sha" != "" ]; then
      if [ -n "$commit_summary" ] && [ "$commit_summary" != "" ] && [ "$commit_summary" != "null" ]; then
        printf "\033[2K\r  %s - %s\n" "$short_sha" "$commit_summary"
      else
        printf "\033[2K\r  %s\n" "$short_sha"
      fi
    else
      printf "\033[2K\r  (no commit info)\n"
    fi
    printf "\033[2K\r\n"
    # Show PR link
    printf "\033[2K\rPR: https://github.com/${REPO}/pull/${PULL_REQUEST}\n"
    # Show timestamp on its own line at the end of output
    printf "\033[2K\rStatus last updated: %s\n" "$timestamp"
  else
    echo "Summary:"
    # Print each check on its own line
    echo "$summary_text"
    # Print status key if there are any statuses to show
    if [ ${#status_key_lines[@]} -gt 0 ]; then
      echo ""
      for key_line in "${status_key_lines[@]}"; do
        echo "  $key_line"
      done
    fi
    echo ""
    echo "Last commit:"
    if [ -n "$short_sha" ] && [ "$short_sha" != "" ]; then
      if [ -n "$commit_summary" ] && [ "$commit_summary" != "" ] && [ "$commit_summary" != "null" ]; then
        echo "  ${short_sha} - ${commit_summary}"
      else
        echo "  ${short_sha}"
      fi
    else
      echo "  (no commit info)"
    fi
    echo ""
    # Show PR link
    echo "PR: https://github.com/${REPO}/pull/${PULL_REQUEST}"
    # Show timestamp on its own line at the end of output
    echo "Status last updated: $timestamp"
  fi
  
  # Return 0 if all checks are complete (ignored in follow mode, which runs until user interrupts)
  if [ "$pending_count" -eq 0 ] && [ "$in_progress_count" -eq 0 ]; then
    return 0
  else
    return 1
  fi
}

# Main execution
if [ -z "$JSON_OUTPUT" ] && [ -z "$FOLLOW" ]; then
  echo "Fetching status checks for PR #${PULL_REQUEST}..."
fi

# Get all status checks from GitHub
GITHUB_CHECKS=$(get_github_status_checks "$PULL_REQUEST")

# Ensure we have valid JSON
if ! echo "$GITHUB_CHECKS" | jq empty 2>/dev/null; then
  GITHUB_CHECKS="[]"
fi

CHECK_COUNT=$(echo "$GITHUB_CHECKS" | jq 'length // 0' 2>/dev/null || echo "0")

# Ensure CHECK_COUNT is numeric
if ! [[ "$CHECK_COUNT" =~ ^[0-9]+$ ]]; then
  CHECK_COUNT=0
fi

if [ "$CHECK_COUNT" -eq 0 ]; then
  if [ -z "$JSON_OUTPUT" ]; then
    echo "No status checks found for PR #${PULL_REQUEST}"
  else
    echo '{"checks": []}'
  fi
  exit 0
fi

# Handle follow mode
if [ -n "$FOLLOW" ]; then
  # Follow mode is incompatible with JSON output and count-only mode
  if [ -n "$JSON_OUTPUT" ] || [ -n "$COUNT_ONLY" ]; then
    echo "Error: --follow cannot be used with --json or --count options"
    exit 1
  fi
  
  # Exit on first Ctrl+C (SIGINT) instead of continuing the loop
  trap 'exit 130' INT
  
  # Loop indefinitely, updating every second until user interrupts (Ctrl+C)
  FIRST_ITERATION=true
  while true; do
    is_update="0"
    if [ "$FIRST_ITERATION" != true ]; then
      is_update="1"
    fi
    
    fetch_and_display_summary "$is_update" "$([ "$FIRST_ITERATION" = true ] && echo "true" || echo "false")"
    
    FIRST_ITERATION=false
    sleep 1
  done
  
  exit 0
fi

# Only print "Found" message if not in follow mode
if [ -z "$JSON_OUTPUT" ] && [ -z "$FOLLOW" ]; then
  echo "Found $CHECK_COUNT status check(s)"
fi

ALL_CHECKS="$GITHUB_CHECKS"

# Enrich CodeQL checks with annotations for failed checks
ALL_CHECKS=$(echo "$ALL_CHECKS" | jq '
  map(
    . as $check |
    if $check.is_codeql == true and ($check.status | ascii_downcase | test("failure|failed|error"; "i")) and ($check.check_run_id != null) then
      # Annotations will be fetched and added in the display section
      $check
    else
      $check
    end
  )
' 2>/dev/null || echo "$ALL_CHECKS")

# Apply filters
FILTERED_CHECKS="$ALL_CHECKS"

# Apply job/check name filter
if [ -n "$JOB_FILTER" ]; then
  FILTERED_CHECKS=$(echo "$FILTERED_CHECKS" | jq --arg filter "$JOB_FILTER" '[.[] | select(.name == $filter or .context == $filter or (.context | contains($filter)))]' 2>/dev/null || echo "$FILTERED_CHECKS")
fi

# Apply status filters (OR logic - if multiple are specified, show checks matching any)
# Map GitHub status values to our filter values
if [ -n "$SHOW_FAILING" ] || [ -n "$SHOW_PASSING" ] || [ -n "$SHOW_IN_PROGRESS" ]; then
  STATUS_FILTER_PARTS=()
  
  if [ -n "$SHOW_FAILING" ]; then
    STATUS_FILTER_PARTS+=("failed|error|failure")
  fi
  
  if [ -n "$SHOW_PASSING" ]; then
    STATUS_FILTER_PARTS+=("success|successful")
  fi
  
  if [ -n "$SHOW_IN_PROGRESS" ]; then
    STATUS_FILTER_PARTS+=("running|pending|in_progress|queued|in_progress|waiting")
  fi
  
  # Join all filter parts with |
  STATUS_FILTER=$(IFS='|'; echo "${STATUS_FILTER_PARTS[*]}")
  
  # Filter checks by status (case-insensitive)
  FILTERED_CHECKS=$(echo "$FILTERED_CHECKS" | jq --arg filter "$STATUS_FILTER" '
    [.[] | select(.status | ascii_downcase | test($filter; "i"))]
  ' 2>/dev/null || echo "$FILTERED_CHECKS")
fi

# Output results
TOTAL=$(echo "$FILTERED_CHECKS" | jq 'length // 0' 2>/dev/null || echo "0")

# Ensure TOTAL is numeric
if ! [[ "$TOTAL" =~ ^[0-9]+$ ]]; then
  TOTAL=0
fi

# Calculate summary counts (for display at the end)
if [ -z "$JSON_OUTPUT" ] && [ -z "$COUNT_ONLY" ]; then
  FAILING_COUNT=$(echo "$FILTERED_CHECKS" | jq '[.[] | select(.status | ascii_downcase | test("failure|failed|error"; "i"))] | length' 2>/dev/null || echo "0")
  EXPECTED_COUNT=$(echo "$FILTERED_CHECKS" | jq '[.[] | select((.type | ascii_downcase) == "expected")] | length' 2>/dev/null || echo "0")
  PENDING_COUNT=$(echo "$FILTERED_CHECKS" | jq '[.[] | select((.status | ascii_downcase | test("pending|queued|waiting"; "i")) and ((.type | ascii_downcase) != "expected"))] | length' 2>/dev/null || echo "0")
  SUCCESS_COUNT=$(echo "$FILTERED_CHECKS" | jq '[.[] | select(.status | ascii_downcase | test("success|successful"; "i"))] | length' 2>/dev/null || echo "0")
  IN_PROGRESS_COUNT=$(echo "$FILTERED_CHECKS" | jq '[.[] | select(.status | ascii_downcase | test("in_progress|running|inprogress"; "i"))] | length' 2>/dev/null || echo "0")
  NEUTRAL_COUNT=$(echo "$FILTERED_CHECKS" | jq '[.[] | select(.status | ascii_downcase | test("neutral|cancelled|canceled|skipped"; "i"))] | length' 2>/dev/null || echo "0")
  UNKNOWN_COUNT=$(echo "$FILTERED_CHECKS" | jq '[.[] | 
    (.type | ascii_downcase) as $type |
    (.status | ascii_downcase) as $status |
    select(
      ($type != "expected") and
      ($status | test("success|successful|failure|failed|error|pending|queued|waiting|in_progress|running|inprogress|neutral|cancelled|canceled|skipped"; "i") | not)
    )
  ] | length' 2>/dev/null || echo "0")
  
  # Ensure counts are numeric
  if ! [[ "$FAILING_COUNT" =~ ^[0-9]+$ ]]; then
    FAILING_COUNT=0
  fi
  if ! [[ "$EXPECTED_COUNT" =~ ^[0-9]+$ ]]; then
    EXPECTED_COUNT=0
  fi
  if ! [[ "$PENDING_COUNT" =~ ^[0-9]+$ ]]; then
    PENDING_COUNT=0
  fi
  if ! [[ "$SUCCESS_COUNT" =~ ^[0-9]+$ ]]; then
    SUCCESS_COUNT=0
  fi
  if ! [[ "$IN_PROGRESS_COUNT" =~ ^[0-9]+$ ]]; then
    IN_PROGRESS_COUNT=0
  fi
  if ! [[ "$NEUTRAL_COUNT" =~ ^[0-9]+$ ]]; then
    NEUTRAL_COUNT=0
  fi
  if ! [[ "$UNKNOWN_COUNT" =~ ^[0-9]+$ ]]; then
    UNKNOWN_COUNT=0
  fi
fi

if [ -n "$COUNT_ONLY" ]; then
  if [ -n "$JSON_OUTPUT" ]; then
    echo "$FILTERED_CHECKS" | jq "{total: length, checks: .}"
  else
    echo "Total: $TOTAL"
  fi
elif [ -n "$JSON_OUTPUT" ]; then
  echo "$FILTERED_CHECKS" | jq '.'
else
  if [ "$TOTAL" -gt 0 ]; then
    for i in $(seq 0 $((TOTAL - 1))); do
      CHECK=$(echo "$FILTERED_CHECKS" | jq ".[$i]" 2>/dev/null)
      
      CHECK_NAME=$(echo "$CHECK" | jq -r '.name // .context // "N/A"')
      CHECK_STATUS=$(echo "$CHECK" | jq -r '.status // "N/A"')
      CHECK_TYPE=$(echo "$CHECK" | jq -r '.type // ""' 2>/dev/null)
      CHECK_DESCRIPTION=$(echo "$CHECK" | jq -r '.description // "N/A"')
      CHECK_URL=$(echo "$CHECK" | jq -r '.html_url // .url // .detailsUrl // "N/A"')
      STARTED_AT=$(echo "$CHECK" | jq -r '.started_at // "N/A"')
      STOPPED_AT=$(echo "$CHECK" | jq -r '.stopped_at // .completed_at // "N/A"')
      IS_CODEQL=$(echo "$CHECK" | jq -r '.is_codeql // false' 2>/dev/null)
      CHECK_RUN_ID=$(echo "$CHECK" | jq -r '.check_run_id // null' 2>/dev/null)

      # Determine emoji based on status and type
      STATUS_LOWER=$(echo "$CHECK_STATUS" | tr '[:upper:]' '[:lower:]')
      TYPE_LOWER=$(echo "$CHECK_TYPE" | tr '[:upper:]' '[:lower:]')
      # Expected checks should show as orange (🟠) even if status is pending
      if [ "$TYPE_LOWER" = "expected" ]; then
        STATUS_EMOJI="🟠"
      else
        case "$STATUS_LOWER" in
          success|successful)
            STATUS_EMOJI="🟢"
            ;;
          failure|failed|error)
            STATUS_EMOJI="🔴"
            ;;
          pending|queued|waiting)
            STATUS_EMOJI="🟡"
            ;;
          in_progress|running|inprogress)
            STATUS_EMOJI="🟠"
            ;;
          neutral|cancelled|canceled|skipped)
            STATUS_EMOJI="⚪"
            ;;
          *)
            STATUS_EMOJI="⚫"
            ;;
        esac
      fi
      
      echo ""
      echo "Check: $CHECK_NAME"
      echo "---"
      echo "Status:           $STATUS_EMOJI $CHECK_STATUS"
      if [ "$CHECK_DESCRIPTION" != "N/A" ] && [ "$CHECK_DESCRIPTION" != "null" ] && [ "$CHECK_DESCRIPTION" != "" ]; then
        echo "Description:      $CHECK_DESCRIPTION"
      fi

      if [ "$STARTED_AT" != "N/A" ] && [ "$STARTED_AT" != "null" ]; then
        echo "Started:          $STARTED_AT"
      fi
      if [ "$STOPPED_AT" != "N/A" ] && [ "$STOPPED_AT" != "null" ]; then
        echo "Completed:        $STOPPED_AT"
      fi
      
      # Calculate duration if both started and completed are available
      if [ "$STARTED_AT" != "N/A" ] && [ "$STARTED_AT" != "null" ] && [ "$STOPPED_AT" != "N/A" ] && [ "$STOPPED_AT" != "null" ]; then
        # Convert ISO 8601 timestamps to seconds since epoch
        # Handle both with and without timezone (Z suffix)
        STARTED_SECONDS=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$STARTED_AT" +%s 2>/dev/null)
        if [ $? -ne 0 ]; then
          # Try without Z suffix
          STARTED_SECONDS=$(date -j -f "%Y-%m-%dT%H:%M:%S" "$STARTED_AT" +%s 2>/dev/null)
        fi
        
        STOPPED_SECONDS=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$STOPPED_AT" +%s 2>/dev/null)
        if [ $? -ne 0 ]; then
          # Try without Z suffix
          STOPPED_SECONDS=$(date -j -f "%Y-%m-%dT%H:%M:%S" "$STOPPED_AT" +%s 2>/dev/null)
        fi
        
        if [ -n "$STARTED_SECONDS" ] && [ -n "$STOPPED_SECONDS" ] && [ "$STARTED_SECONDS" != "" ] && [ "$STOPPED_SECONDS" != "" ]; then
          DURATION_SECONDS=$((STOPPED_SECONDS - STARTED_SECONDS))
          
          # Format duration in human-readable format
          if [ "$DURATION_SECONDS" -lt 0 ]; then
            DURATION="N/A (invalid)"
          elif [ "$DURATION_SECONDS" -lt 60 ]; then
            DURATION="${DURATION_SECONDS}s"
          elif [ "$DURATION_SECONDS" -lt 3600 ]; then
            MINUTES=$((DURATION_SECONDS / 60))
            SECONDS=$((DURATION_SECONDS % 60))
            if [ "$SECONDS" -eq 0 ]; then
              DURATION="${MINUTES}m"
            else
              DURATION="${MINUTES}m ${SECONDS}s"
            fi
          else
            HOURS=$((DURATION_SECONDS / 3600))
            REMAINING_SECONDS=$((DURATION_SECONDS % 3600))
            MINUTES=$((REMAINING_SECONDS / 60))
            SECONDS=$((REMAINING_SECONDS % 60))
            if [ "$MINUTES" -eq 0 ] && [ "$SECONDS" -eq 0 ]; then
              DURATION="${HOURS}h"
            elif [ "$SECONDS" -eq 0 ]; then
              DURATION="${HOURS}h ${MINUTES}m"
            else
              DURATION="${HOURS}h ${MINUTES}m ${SECONDS}s"
            fi
          fi
          
          echo "Duration:         $DURATION"
        fi
      fi
      
      if [ "$CHECK_URL" != "N/A" ] && [ "$CHECK_URL" != "null" ] && [ "$CHECK_URL" != "" ]; then
        echo "URL:              $CHECK_URL"
      fi
      
      # Show CodeQL annotations for failed checks (unless --hide-job-output is set)
      if [ "$IS_CODEQL" = "true" ] && [ -z "$HIDE_JOB_OUTPUT" ] && [ "$CHECK_STATUS" != "success" ] && [ "$CHECK_STATUS" != "successful" ] && [ "$CHECK_STATUS" != "N/A" ] && [ "$CHECK_RUN_ID" != "null" ] && [ -n "$CHECK_RUN_ID" ]; then
        # Fetch annotations for this CodeQL check run
        ANNOTATIONS=$(get_check_run_annotations "$CHECK_RUN_ID" 2>/dev/null)
        if [ $? -eq 0 ] && [ -n "$ANNOTATIONS" ] && echo "$ANNOTATIONS" | jq empty 2>/dev/null; then
          ANNOTATION_COUNT=$(echo "$ANNOTATIONS" | jq 'length' 2>/dev/null || echo "0")
          if [ "$ANNOTATION_COUNT" -gt 0 ]; then
            echo ""
            echo "Security Alerts:"
            
            # Group annotations by severity level (annotation_level: failure, warning, notice)
            # Map to more readable severity names
            HIGH_ALERTS=$(echo "$ANNOTATIONS" | jq '[.[] | select(.annotation_level == "failure")]' 2>/dev/null)
            MEDIUM_ALERTS=$(echo "$ANNOTATIONS" | jq '[.[] | select(.annotation_level == "warning")]' 2>/dev/null)
            LOW_ALERTS=$(echo "$ANNOTATIONS" | jq '[.[] | select(.annotation_level == "notice")]' 2>/dev/null)
            
            HIGH_COUNT=$(echo "$HIGH_ALERTS" | jq 'length' 2>/dev/null || echo "0")
            MEDIUM_COUNT=$(echo "$MEDIUM_ALERTS" | jq 'length' 2>/dev/null || echo "0")
            LOW_COUNT=$(echo "$LOW_ALERTS" | jq 'length' 2>/dev/null || echo "0")
            
            if [ "$HIGH_COUNT" -gt 0 ] || [ "$MEDIUM_COUNT" -gt 0 ] || [ "$LOW_COUNT" -gt 0 ]; then
              if [ "$HIGH_COUNT" -gt 0 ]; then
                echo "  High: $HIGH_COUNT"
              fi
              if [ "$MEDIUM_COUNT" -gt 0 ]; then
                echo "  Medium: $MEDIUM_COUNT"
              fi
              if [ "$LOW_COUNT" -gt 0 ]; then
                echo "  Low: $LOW_COUNT"
              fi
              echo ""
            fi
            
            # Display annotations, prioritizing high severity first
            if [ "$HIGH_COUNT" -gt 0 ]; then
              echo "$HIGH_ALERTS" | jq -c '.[]' 2>/dev/null | while IFS= read -r annotation; do
                path=$(echo "$annotation" | jq -r '.path // "N/A"' 2>/dev/null)
                start_line=$(echo "$annotation" | jq -r '.start_line // "N/A"' 2>/dev/null)
                end_line=$(echo "$annotation" | jq -r '.end_line // "N/A"' 2>/dev/null)
                title=$(echo "$annotation" | jq -r '.title // "Security Alert"' 2>/dev/null)
                message=$(echo "$annotation" | jq -r '.message // "No message"' 2>/dev/null)
                
                if [ "$start_line" = "$end_line" ]; then
                  line_info="line $start_line"
                else
                  line_info="lines $start_line-$end_line"
                fi
                
                echo "  🔴 $path:$line_info"
                echo "     $title"
                if [ "$message" != "No message" ] && [ -n "$message" ]; then
                  # Truncate long messages to first 200 characters
                  message_len=$(echo "$message" | wc -c | tr -d ' ')
                  if [ "$message_len" -gt 200 ]; then
                    message=$(echo "$message" | cut -c1-200)"..."
                  fi
                  echo "     $message"
                fi
                echo ""
              done
            fi
            
            if [ "$MEDIUM_COUNT" -gt 0 ]; then
              echo "$MEDIUM_ALERTS" | jq -c '.[]' 2>/dev/null | while IFS= read -r annotation; do
                path=$(echo "$annotation" | jq -r '.path // "N/A"' 2>/dev/null)
                start_line=$(echo "$annotation" | jq -r '.start_line // "N/A"' 2>/dev/null)
                end_line=$(echo "$annotation" | jq -r '.end_line // "N/A"' 2>/dev/null)
                title=$(echo "$annotation" | jq -r '.title // "Security Alert"' 2>/dev/null)
                message=$(echo "$annotation" | jq -r '.message // "No message"' 2>/dev/null)
                
                if [ "$start_line" = "$end_line" ]; then
                  line_info="line $start_line"
                else
                  line_info="lines $start_line-$end_line"
                fi
                
                echo "  🟡 $path:$line_info"
                echo "     $title"
                if [ "$message" != "No message" ] && [ -n "$message" ]; then
                  message_len=$(echo "$message" | wc -c | tr -d ' ')
                  if [ "$message_len" -gt 200 ]; then
                    message=$(echo "$message" | cut -c1-200)"..."
                  fi
                  echo "     $message"
                fi
                echo ""
              done
            fi
            
            if [ "$LOW_COUNT" -gt 0 ]; then
              echo "$LOW_ALERTS" | jq -c '.[]' 2>/dev/null | while IFS= read -r annotation; do
                path=$(echo "$annotation" | jq -r '.path // "N/A"' 2>/dev/null)
                start_line=$(echo "$annotation" | jq -r '.start_line // "N/A"' 2>/dev/null)
                end_line=$(echo "$annotation" | jq -r '.end_line // "N/A"' 2>/dev/null)
                title=$(echo "$annotation" | jq -r '.title // "Security Alert"' 2>/dev/null)
                message=$(echo "$annotation" | jq -r '.message // "No message"' 2>/dev/null)
                
                if [ "$start_line" = "$end_line" ]; then
                  line_info="line $start_line"
                else
                  line_info="lines $start_line-$end_line"
                fi
                
                echo "  ⚪ $path:$line_info"
                echo "     $title"
                if [ "$message" != "No message" ] && [ -n "$message" ]; then
                  message_len=$(echo "$message" | wc -c | tr -d ' ')
                  if [ "$message_len" -gt 200 ]; then
                    message=$(echo "$message" | cut -c1-200)"..."
                  fi
                  echo "     $message"
                fi
                echo ""
              done
            fi
          fi
        fi
      fi
      
      echo ""
    done
    
    # Display summary at the end
    echo "---"
    echo "Summary:"
    # List each check with its status emoji
    SUMMARY_LINES=$(echo "$FILTERED_CHECKS" | jq -r '.[] | 
      (.type | ascii_downcase) as $type |
      (.status | ascii_downcase) as $status |
      (if $type == "expected" then "🟠"
       elif $status == "success" or $status == "successful" then "🟢"
       elif $status == "failure" or $status == "failed" or $status == "error" then "🔴"
       elif $status == "pending" or $status == "queued" or $status == "waiting" then "🟡"
       elif $status == "in_progress" or $status == "running" or $status == "inprogress" then "🟠"
       elif $status == "neutral" or $status == "cancelled" or $status == "canceled" or $status == "skipped" then "⚪"
       else "⚫" end) as $emoji |
      "\($emoji)  Check: \(.name // .context // "N/A")"
    ' 2>/dev/null)
    
    if [ -n "$SUMMARY_LINES" ] && [ "$SUMMARY_LINES" != "" ]; then
      echo "$SUMMARY_LINES"
    else
      echo "No checks found"
    fi
    
    # Build status key lines with only statuses that have counts > 0
    if [ -z "$JSON_OUTPUT" ] && [ -z "$COUNT_ONLY" ]; then
      STATUS_KEY_LINES=()
      if [ "$SUCCESS_COUNT" -gt 0 ]; then
        STATUS_KEY_LINES+=("🟢 Success ($SUCCESS_COUNT)")
      fi
      if [ "$IN_PROGRESS_COUNT" -gt 0 ] || [ "$EXPECTED_COUNT" -gt 0 ]; then
        TOTAL_IN_PROGRESS=$((IN_PROGRESS_COUNT + EXPECTED_COUNT))
        STATUS_KEY_LINES+=("🟠 In Progress/Expected ($TOTAL_IN_PROGRESS)")
      fi
      if [ "$FAILING_COUNT" -gt 0 ]; then
        STATUS_KEY_LINES+=("🔴 Failed ($FAILING_COUNT)")
      fi
      if [ "$PENDING_COUNT" -gt 0 ]; then
        STATUS_KEY_LINES+=("🟡 Pending ($PENDING_COUNT)")
      fi
      if [ "$NEUTRAL_COUNT" -gt 0 ]; then
        STATUS_KEY_LINES+=("⚪ Neutral/Cancelled ($NEUTRAL_COUNT)")
      fi
      if [ "$UNKNOWN_COUNT" -gt 0 ]; then
        STATUS_KEY_LINES+=("⚫ Unknown ($UNKNOWN_COUNT)")
      fi
      
      if [ ${#STATUS_KEY_LINES[@]} -gt 0 ]; then
        echo ""
        for key_line in "${STATUS_KEY_LINES[@]}"; do
          echo "  $key_line"
        done
      fi
    fi
    echo ""
    
    # Get last commit SHA and summary from origin (via GitHub API)
    PR_DATA=$(gh api "repos/${REPO}/pulls/${PULL_REQUEST}" 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$PR_DATA" ]; then
      HEAD_SHA=$(echo "$PR_DATA" | jq -r '.head.sha // empty' 2>/dev/null)
      if [ -n "$HEAD_SHA" ] && [ "$HEAD_SHA" != "null" ] && [ "$HEAD_SHA" != "" ]; then
        # Get short SHA (first 7 characters)
        SHORT_SHA=$(echo "$HEAD_SHA" | cut -c1-7)
        
        # Get commit message summary (first line) from GitHub API
        COMMIT_DATA=$(gh api "repos/${REPO}/commits/${HEAD_SHA}" 2>/dev/null)
        if [ $? -eq 0 ] && [ -n "$COMMIT_DATA" ]; then
          COMMIT_SUMMARY=$(echo "$COMMIT_DATA" | jq -r '.commit.message // ""' 2>/dev/null | head -n1 | sed 's/\r$//')
          
          echo "Last commit:"
          if [ -n "$COMMIT_SUMMARY" ] && [ "$COMMIT_SUMMARY" != "" ] && [ "$COMMIT_SUMMARY" != "null" ]; then
            echo "  ${SHORT_SHA} - ${COMMIT_SUMMARY}"
          else
            echo "  ${SHORT_SHA}"
          fi
        else
          echo "Last commit:"
          echo "  ${SHORT_SHA}"
        fi
      fi
    fi
    echo ""
    
    echo "PR: https://github.com/${REPO}/pull/${PULL_REQUEST}"
      else
        echo "No checks found matching the specified filters."
      fi
    fi
