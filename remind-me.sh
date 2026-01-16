#!/bin/bash
# Quick reminder script for common tasks

# Colors for better readability
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Prediction Contests - Quick Reminders ===${NC}\n"

# Check if a specific section is requested
if [ "$1" == "run" ]; then
    echo -e "${GREEN}Running the site locally:${NC}"
    echo "  bundle exec jekyll serve"
    echo "  Then visit: http://localhost:4000/prediction-contests"
    echo ""

elif [ "$1" == "post" ]; then
    echo -e "${GREEN}Creating a new blog post:${NC}"
    echo "  1. Create file: _posts/$(date +%Y-%m-%d)-your-title.md"
    echo "  2. Add front matter:"
    echo "     ---"
    echo "     layout: post"
    echo "     title: \"Your Title\""
    echo "     subtitle: \"Subtitle here\""
    echo "     date: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "     background: '/img/bg-post.jpg'"
    echo "     ---"
    echo ""

elif [ "$1" == "leaderboard" ]; then
    echo -e "${GREEN}Updating leaderboard:${NC}"
    echo "  Edit the .md file with a markdown table:"
    echo "  {:.thead-dark .table-striped .table-bordered .table-sm }"
    echo "  | Name | Location | Score |"
    echo "  |:-----|:---------|------:|"
    echo "  | Player 1 | USA | 45 |"
    echo ""

elif [ "$1" == "deploy" ]; then
    echo -e "${GREEN}Deploying to GitHub Pages:${NC}"
    echo "  git add ."
    echo "  git commit -m \"Your message\""
    echo "  git push origin main"
    echo "  Live at: https://ram-n.github.io/prediction-contests"
    echo ""

elif [ "$1" == "archive" ]; then
    echo -e "${GREEN}Archiving current contest:${NC}"
    echo "  1. Move contest to past: mv current-contest/ past/current-contest/"
    echo "  2. Update Hall of Fame: vim past/hof.md"
    echo "  3. Update past index: vim past/index.md"
    echo "  4. Create final blog post announcing winner"
    echo ""
    echo "  Full guide: cat docs/archive-current-contest.md"
    echo "              less docs/archive-current-contest.md"
    echo ""

else
    echo "Usage: ./remind-me.sh [command]"
    echo ""
    echo "Commands:"
    echo "  run         - How to run the site locally"
    echo "  post        - Create a new blog post"
    echo "  leaderboard - Update leaderboard tables"
    echo "  deploy      - Deploy to GitHub Pages"
    echo "  archive     - Archive a completed contest"
    echo ""
    echo "Or view full guide: cat docs/QUICKSTART.md"
    echo "                    less docs/QUICKSTART.md"
    echo ""
fi
