/**
 * Word GPT Plus - Main Entry Point
 * This file serves as the main entry point for the Word GPT Plus add-in
 */

// Import core dependencies
import './polyfills.js';
import './simple-taskpane.js';

// Log initialization
console.log('Word GPT Plus initializing...');

// Initialize application when Office is ready
Office.onReady(info => {
    if (info.host === Office.HostType.Word) {
        console.log('Word GPT Plus initialized in Word');
        document.getElementById('app-loading')?.classList.add('hidden');
        document.getElementById('app-container')?.classList.remove('hidden');
    } else {
        console.log('Word GPT Plus running in unsupported host');
        document.getElementById('app-loading')?.classList.add('hidden');
        document.getElementById('unsupported-host')?.classList.remove('hidden');
    }
});
