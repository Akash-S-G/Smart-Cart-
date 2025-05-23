# Install dependencies
npm install

# Create necessary directories
mkdir -p public/images
mkdir -p src/assets
mkdir -p src/hooks
mkdir -p src/utils
mkdir -p src/services

# Initialize React app with TypeScript
npx create-react-app . --template typescript

# Install additional dependencies
npm install @headlessui/react @heroicons/react @mapbox/mapbox-gl-geocoder @tailwindcss/forms axios chart.js jwt-decode mapbox-gl react-chartjs-2 react-hot-toast react-icons react-router-dom react-webcam socket.io-client zustand @types/mapbox-gl @types/mapbox__mapbox-gl-geocoder

# Install dev dependencies
npm install -D autoprefixer postcss tailwindcss @types/react-webcam

# Initialize Tailwind CSS
npx tailwindcss init -p 