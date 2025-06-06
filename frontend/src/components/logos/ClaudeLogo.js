import React from 'react';

const ClaudeLogo = ({ size = 24, color = '#6b5ce7' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="2" y="4" width="20" height="16" rx="3" stroke={color} strokeWidth="2"/>
    <path d="M7 9.5C7 9.5 9 12 12 12C15 12 17 9.5 17 9.5" stroke={color} strokeWidth="2" strokeLinecap="round"/>
    <circle cx="8" cy="10" r="1" fill={color}/>
    <circle cx="16" cy="10" r="1" fill={color}/>
  </svg>
);

export default ClaudeLogo;
