
#!/bin/bash

poetry build
cd dist
tar -xvzf server-0.1.0.tar.gz
cd server-0.1.0
poetry export --without-hashes --format requirements.txt --output server/requirements.txt
cd ../../web
npm run build
mkdir ../dist/server-0.1.0/server/static
cp  -R  dist/* ../dist/server-0.1.0/server/static
cd ../dist/server-0.1.0/server
vercel .
