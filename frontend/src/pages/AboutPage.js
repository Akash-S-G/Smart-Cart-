import React from 'react';

const AboutPage = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">About Smart Cart AI</h1>
      <div className="prose max-w-none">
        <p className="mb-4">
          Smart Cart AI is an innovative shopping system that combines artificial intelligence
          with real-time product detection to enhance your shopping experience.
        </p>
        <p className="mb-4">
          Our system uses advanced computer vision technology and ESP32-CAM integration
          to provide real-time product recognition and tracking.
        </p>
      </div>
    </div>
  );
};

export default AboutPage; 