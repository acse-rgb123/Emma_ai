import React from 'react';

const GeminiLogo = ({ size = 24, color = '#4285f4' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 2L14.5 7L20 7.5L16 11.5L17 17L12 14.5L7 17L8 11.5L4 7.5L9.5 7L12 2Z" fill={color} opacity="0.3"/>
    <path d="M12 8L13.5 11L17 11.5L14.5 14L15 17.5L12 16L9 17.5L9.5 14L7 11.5L10.5 11L12 8Z" fill={color}/>
  </svg>
);

export default GeminiLogo;
