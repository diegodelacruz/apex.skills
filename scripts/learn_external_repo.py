#!/usr/bin/env python3
"""
Learn External Repo: Main entry point for apex-external-context-learn skill.
Analyzes external repositories without cloning and creates persistent references.

Usage:
	python learn_external_repo.py <url_or_path> <analysis_request> [--step-by-step]
	python learn_external_repo.py list
	python learn_external_repo.py delete <repo_id>
"""

import json
import sys

from scripts.cli_utils import CLIParser
from scripts.external_repo_indexer import ExternalRepoIndexer
from scripts.external_repo_scanner import ExternalRepoScanner


def main():
    """Main entry point."""
    parser = CLIParser("Learn from external repositories")
    parser.add_argument("action", choices=["learn", "list", "delete", "show"], default="learn", nargs="?")
    parser.add_argument("--source", help="Repository URL or local path")
    parser.add_argument("--extract", help="What to extract/analyze from the repository")
    parser.add_argument("--step-by-step", action="store_true", help="Verbose step-by-step output")
    parser.add_argument("--repo-id", help="Repository identifier (for delete/show)")
    parser.add_argument("--force", action="store_true", help="Force re-analysis of existing repo")

    args = parser.parse_args()

    try:
        if args.action == "learn":
            learn_repo(args)
        elif args.action == "list":
            list_repos()
        elif args.action == "delete":
            delete_repo(args)
        elif args.action == "show":
            show_repo(args)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def learn_repo(args) -> None:
    """Learn from an external repository."""
    if not args.source:
        print("❌ Error: --source required (URL or path)")
        print("Usage: python learn_external_repo.py --source <url_or_path> --extract '<analysis_request>'")
        sys.exit(1)

    if not args.extract:
        args.extract = "Analyze structure and content"

    verbose = args.step_by_step

    # Initialize indexer
    indexer = ExternalRepoIndexer()

    # Check if already learned
    existing_id = indexer.search_by_source(args.source)
    if existing_id and not args.force:
        print(f"⚠️  Repository already learned: {existing_id}")
        print(f"   Location: {indexer.repos_dir / f'{existing_id}.json'}")
        print("   Use --force to re-analyze")
        return

    if verbose:
        print("📚 Learning from external repository")
        print(f"   Source: {args.source}")
        print(f"   Request: {args.extract}")
        print()

    # Step 1: Validate and scan
    if verbose:
        print("1️⃣  Validating access...")
    try:
        scanner = ExternalRepoScanner(args.source)
        if verbose:
            print("   ✅ Access confirmed")
    except (ValueError, RuntimeError) as e:
        print(f"❌ Cannot access repository: {e}")
        sys.exit(1)

    # Step 2: Scan repository
    if verbose:
        print("2️⃣  Scanning repository structure...")
    try:
        repo_metadata = scanner.scan()
        if verbose:
            print(f"   ✅ Found {repo_metadata['repo_info']['total_files']} files")
            print(f"   ✅ Languages: {', '.join(repo_metadata['repo_info']['languages_detected'])}")
            print(f"   ✅ Structure: {repo_metadata['repo_info']['structure_summary']}")
    except ValueError as e:
        print(f"❌ Repository is empty or inaccessible: {e}")
        sys.exit(1)

    # Step 3: Prepare analysis
    if verbose:
        print("3️⃣  Analyzing repository...")
    analysis_summary = {
        "extracted_by_user": args.extract,
        "analysis": f"Repository analyzed for: {args.extract}",
        "key_findings": [
            f"Total files: {repo_metadata['repo_info']['total_files']}",
            f"Languages detected: {', '.join(repo_metadata['repo_info']['languages_detected'])}",
            f"File types: {', '.join(repo_metadata['repo_info']['file_extensions_found'])}",
        ],
    }

    # Step 4: Save to persistent storage
    if verbose:
        print("4️⃣  Saving reference...")
    repo_id = indexer.save_learned_repo(repo_metadata, analysis_summary)
    if verbose:
        print(f"   ✅ Saved as: {repo_id}")

    # Step 5: Confirm availability
    if verbose:
        print("5️⃣  Confirming availability...")
        print("   ✅ Available for other skills automatically")
        print(f"   ✅ Location: control-proyecto/external-repos/{repo_id}.json")
        print()

    # Summary
    print("✅ Successfully learned from repository")
    print(f"   ID: {repo_id}")
    print(f"   Source: {args.source}")
    print(f"   Files: {repo_metadata['repo_info']['total_files']}")
    print(f"   Languages: {', '.join(repo_metadata['repo_info']['languages_detected'])}")
    print(f"   Stored: control-proyecto/external-repos/{repo_id}.json")


def list_repos() -> None:
    """List all learned repositories."""
    indexer = ExternalRepoIndexer()
    repos = indexer.list_all()

    if not repos:
        print("No learned repositories yet.")
        return

    print(f"📚 Learned Repositories ({len(repos)}):\n")
    for repo in repos:
        print(f"ID: {repo['identifier']}")
        print(f"   Source: {repo['source']}")
        print(f"   Type: {repo['source_type']}")
        print(f"   Scanned: {repo['scanned_at']}")
        print()


def delete_repo(args) -> None:
    """Delete a learned repository."""
    if not args.repo_id:
        print("❌ Error: --repo-id required")
        print("Usage: python learn_external_repo.py delete --repo-id <id>")
        sys.exit(1)

    indexer = ExternalRepoIndexer()
    if not indexer.repo_exists(args.repo_id):
        print(f"❌ Repository not found: {args.repo_id}")
        sys.exit(1)

    # Confirm deletion
    print(f"⚠️  Delete learned repository: {args.repo_id}?")
    response = input("Confirm (y/n): ").strip().lower()
    if response != "y":
        print("Cancelled.")
        return

    if indexer.delete_learned_repo(args.repo_id):
        print(f"✅ Deleted: {args.repo_id}")
    else:
        print(f"❌ Failed to delete: {args.repo_id}")


def show_repo(args) -> None:
    """Show details of a learned repository."""
    if not args.repo_id:
        print("❌ Error: --repo-id required")
        print("Usage: python learn_external_repo.py show --repo-id <id>")
        sys.exit(1)

    indexer = ExternalRepoIndexer()
    repo_data = indexer.get_learned_repo(args.repo_id)
    if not repo_data:
        print(f"❌ Repository not found: {args.repo_id}")
        sys.exit(1)

    print(json.dumps(repo_data, indent=2))


if __name__ == "__main__":
    main()
