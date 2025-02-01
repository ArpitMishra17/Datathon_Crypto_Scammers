import React from 'react';
import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';

export default function Portal({ children }) {
  const [portalElement, setPortalElement] = useState(null);

  useEffect(() => {
    // Create a div element for the portal
    const element = document.createElement('div');
    document.body.appendChild(element);
    setPortalElement(element);

    // Cleanup on unmount
    return () => {
      document.body.removeChild(element);
    };
  }, []);

  if (!portalElement) return null;

  return createPortal(children, portalElement);
}