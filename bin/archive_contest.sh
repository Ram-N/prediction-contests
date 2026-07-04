#!/bin/bash
# Archive current contest and prepare for new one
# This script automates the transition between contests

set -e  # Exit on error

echo "=== Contest Archival Script ==="
echo ""

# 1. Read current contest slug from _config.yml
SLUG=$(grep -A1 "^contest:" _config.yml | grep "slug:" | awk '{print $2}' | tr -d '"')
CONTEST_NAME=$(grep -A2 "^contest:" _config.yml | grep "name:" | sed 's/.*name: "\(.*\)"/\1/')

if [ -z "$SLUG" ]; then
  echo "Error: Could not read contest slug from _config.yml"
  exit 1
fi

echo "Current contest: $CONTEST_NAME ($SLUG)"
echo ""
read -p "Are you sure you want to archive this contest? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Archival cancelled."
  exit 0
fi

# 2. Bake variables into active-contest/ files
echo ""
echo "Step 1: Baking liquid variables into active-contest/ files..."
find active-contest/ -name "*.md" -exec sed -i \
  -e "s|{{ site.contest.slug }}|$SLUG|g" \
  -e "s|{{ site.baseurl }}/{{ site.contest.slug }}|/prediction-contests/$SLUG|g" \
  -e "s|{{ '/' | append: site.contest.slug | append: '/' | relative_url }}|/prediction-contests/$SLUG/|g" \
  -e "s|{{ '/' | append: site.contest.slug | append: '/leaderboard' | relative_url }}|/prediction-contests/$SLUG/leaderboard|g" \
  -e "s|{{ '/' | append: site.contest.slug | append: '/predictions' | relative_url }}|/prediction-contests/$SLUG/predictions|g" \
  -e "s|{{ '/' | append: site.contest.slug | append: '/rules' | relative_url }}|/prediction-contests/$SLUG/rules|g" \
  -e "s|{{ '/' | append: site.contest.slug | append: '/entry' | relative_url }}|/prediction-contests/$SLUG/entry|g" \
  {} \;
echo "✅ Variables baked successfully"

# 3. Move to past/
echo ""
echo "Step 2: Moving active-contest/ to past/$SLUG/..."
git mv active-contest/ past/$SLUG/
echo "✅ Moved to past/$SLUG/"

# 4. Prompt for new contest details
echo ""
echo "Step 3: Setting up new contest..."
read -p "New contest slug (e.g., wc-2030): " NEW_SLUG
read -p "New contest short name (e.g., WC 2030): " NEW_NAME
read -p "New contest full title (e.g., World Cup 2030 Prediction Contest): " NEW_FULL_TITLE
read -p "Background image path (e.g., /img/bg_wc2030.webp): " NEW_BG

# 5. Update _config.yml
echo ""
echo "Step 4: Updating _config.yml..."
sed -i \
  -e "s|slug: \"$SLUG\"|slug: \"$NEW_SLUG\"|" \
  -e "s|name: \".*\"|name: \"$NEW_NAME\"|" \
  -e "s|full_title: \".*\"|full_title: \"$NEW_FULL_TITLE\"|" \
  -e "s|background: \".*\"|background: \"$NEW_BG\"|" \
  _config.yml
echo "✅ Updated _config.yml"

# 6. Create new active-contest/ from templates
echo ""
echo "Step 5: Creating new active-contest/ from templates..."
if [ -d "templates/active-contest" ]; then
  cp -r templates/active-contest/ ./
  echo "✅ Created active-contest/ from templates"
else
  echo "⚠️  Warning: templates/active-contest/ not found"
  echo "   You'll need to manually create active-contest/ files"
fi

echo ""
echo "=== Archival Complete ==="
echo ""
echo "✅ Archived $SLUG to past/$SLUG/"
echo "✅ Created new active-contest/ for $NEW_SLUG"
echo ""
echo "Next steps:"
echo "1. Update active-contest/*.md files with contest-specific content"
echo "2. Create active-contest/data/ with predictions, matches, schedule CSVs"
echo "3. Update scripts/contest_config.json with new contest details"
echo "4. Review all changes"
echo "5. Commit: git add . && git commit -m 'chore: archive $SLUG and start $NEW_SLUG'"
echo "6. Push: git push"
echo ""
