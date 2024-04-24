# Step 1: Copy all content of ./src to ./package, excluding items in .gitignore
# Use rsync to respect .gitignore
rsync -av --exclude-from='../../.gitignore' ../../server/src/ ./package/

# Step 2: Install Python packages specified in requirements.txt into ./package/python
# Ensure the target directory exists
mkdir -p ./package/python
cd ./package
pip install -r requirements.txt -t ./python

# Step 3: Zip the contents of ./package into package.zip
# Move into the package directory and zip its contents

zip -r ../package.zip .
cd ..

echo "Packaging completed successfully."