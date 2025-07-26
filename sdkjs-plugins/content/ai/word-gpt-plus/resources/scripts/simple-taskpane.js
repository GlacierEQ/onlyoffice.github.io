/**
 * Word GPT Plus - Simple Taskpane
 * Basic implementation of the taskpane functionality
 */

import simpleApiClient from './simple-api-client.js';
import simpleDocumentManager from './simple-document-manager.js';
import simpleConfig from './simple-config.js';
import modelManager from './model-manager.js';

class SimpleTaskpane {
    constructor() {
        // UI elements
        this.elements = {
            prompt: null,
            result: null,
            generate: null,
            insert: null,
            clear: null,
            status: null,
            templates: null,
            settingsToggle: null,
            settingsPanel: null,
            localEndpoint: null,
            modelName: null,
            saveSettings: null
        };

        // State
        this.state = {
            isGenerating: false,
            selectedTemplate: null,
            lastResult: null
        };

        // Bind methods
        this.init = this.init.bind(this);
        this.handleGenerate = this.handleGenerate.bind(this);
        this.handleInsert = this.handleInsert.bind(this);
        this.handleClear = this.handleClear.bind(this);
        this.handleTemplateClick = this.handleTemplateClick.bind(this);
        this.toggleSettings = this.toggleSettings.bind(this);
        this.saveSettings = this.saveSettings.bind(this);
    }

    /**
     * Initialize the taskpane
     * @returns {Promise<boolean>} Initialization result
     */
    async init() {
        try {
            // Get UI elements
            this.getElements();

            // Add event listeners
            this.addEventListeners();

            // Load settings from storage
            this.loadSettings();

            // Render templates
            this.renderTemplates();

            console.log('Simple taskpane initialized');
            return true;
        } catch (error) {
            console.error('Error initializing taskpane:', error);
            this.showStatus('Failed to initialize taskpane', 'error');
            return false;
        }
    }

    /**
     * Get references to UI elements
     */
    getElements() {
        this.elements.prompt = document.getElementById('prompt');
        this.elements.result = document.getElementById('result');
        this.elements.generate = document.getElementById('generate');
        this.elements.insert = document.getElementById('insert');
        this.elements.clear = document.getElementById('clear-btn');
        this.elements.status = document.getElementById('status');
        this.elements.templates = document.getElementById('templates');
        this.elements.settingsToggle = document.getElementById('settings-toggle');
        this.elements.settingsPanel = document.getElementById('settings-panel');
        this.elements.localEndpoint = document.getElementById('local-endpoint');
        this.elements.modelName = document.getElementById('model-name');
        this.elements.saveSettings = document.getElementById('save-settings');

        // Verify required elements
        if (!this.elements.prompt || !this.elements.result || !this.elements.generate) {
            throw new Error('Required UI elements not found');
        }
    }

    /**
     * Add event listeners to UI elements
     */
    addEventListeners() {
        this.elements.generate.addEventListener('click', this.handleGenerate);
        this.elements.insert.addEventListener('click', this.handleInsert);
        this.elements.clear.addEventListener('click', this.handleClear);
        this.elements.settingsToggle.addEventListener('click', this.toggleSettings);
        this.elements.saveSettings.addEventListener('click', this.saveSettings);
    }

    /**
     * Load settings from storage
     */
    loadSettings() {
        // Update UI with current API settings
        this.elements.localEndpoint.value = simpleApiClient.localEndpoint || '';
        this.elements.modelName.value = simpleApiClient.model || '';
    }

    /**
     * Render template buttons
     */
    renderTemplates() {
        const templates = simpleConfig.ui.templates;
        if (!templates) return;

        this.elements.templates.innerHTML = '';

        templates.forEach(template => {
            const button = document.createElement('button');
            button.className = 'template-btn';
            button.textContent = template.name;
            button.dataset.templateId = template.id;
            button.addEventListener('click', () => this.handleTemplateClick(template));

            this.elements.templates.appendChild(button);
        });
    }

    /**
     * Handle template selection
     * @param {Object} template - Selected template
     */
    handleTemplateClick(template) {
        // Update selected template
        this.state.selectedTemplate = template.id;

        // Update UI
        const templateButtons = document.querySelectorAll('.template-btn');
        templateButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.templateId === template.id);
        });

        // Set prompt text
        this.elements.prompt.value = template.prompt;
    }

    /**
     * Handle generate button click
     */
    async handleGenerate() {
        if (this.state.isGenerating) return;

        try {
            const prompt = this.elements.prompt.value.trim();
            if (!prompt) {
                this.showStatus('Please enter a prompt', 'error');
                return;
            }

            // Update UI state
            this.state.isGenerating = true;
            this.elements.generate.disabled = true;
            this.elements.generate.textContent = 'Generating...';
            this.elements.result.innerHTML = 'Please wait, generating content...';

            // Generate text
            const result = await modelManager.generateText(prompt, {
                demoMode: true // Use demo mode for initial testing
            });

            // Update result
            this.elements.result.innerHTML = result;
            this.state.lastResult = result;

            // Show status
            this.showStatus('Content generated successfully', 'success');

        } catch (error) {
            this.elements.result.innerHTML = `Error: ${error.message}`;
            this.showStatus('Failed to generate content', 'error');
        } finally {
            // Reset UI state
            this.state.isGenerating = false;
            this.elements.generate.disabled = false;
            this.elements.generate.textContent = 'Generate';
        }
    }

    /**
     * Handle insert button click
     */
    async handleInsert() {
        if (!this.state.lastResult) {
            this.showStatus('No content to insert', 'error');
            return;
        }

        try {
            // Insert text into document
            await simpleDocumentManager.insertText(this.state.lastResult);
            this.showStatus('Content inserted into document', 'success');
        } catch (error) {
            this.showStatus('Failed to insert content: ' + error.message, 'error');
        }
    }

    /**
     * Handle clear button click
     */
    handleClear() {
        this.elements.prompt.value = '';
        this.elements.result.innerHTML = 'Generated text will appear here...';
        this.state.lastResult = null;

        // Clear template selection
        const templateButtons = document.querySelectorAll('.template-btn');
        templateButtons.forEach(btn => btn.classList.remove('active'));
        this.state.selectedTemplate = null;
    }

    /**
     * Toggle settings panel
     */
    toggleSettings() {
        const panel = this.elements.settingsPanel;
        const isVisible = panel.style.display !== 'none';

        panel.style.display = isVisible ? 'none' : 'block';
    }

    /**
     * Save settings
     */
    saveSettings() {
        try {
            const endpoint = this.elements.localEndpoint.value.trim();
            const model = this.elements.modelName.value.trim();

            simpleApiClient.setLocalConfig(endpoint, model);

            this.showStatus('Settings saved successfully', 'success');
            this.toggleSettings();
        } catch (error) {
            this.showStatus('Failed to save settings: ' + error.message, 'error');
        }
    }

    /**
     * Show status message
     * @param {string} message - Status message
     * @param {string} type - Message type (success, error, info)
     */
    showStatus(message, type = 'info') {
        const statusEl = this.elements.status;
        if (!statusEl) return;

        statusEl.textContent = message;
        statusEl.className = 'status-message';
        statusEl.classList.add(`status-${type}`);
        statusEl.style.display = 'block';

        // Hide after 5 seconds
        setTimeout(() => {
            statusEl.style.display = 'none';
        }, 5000);
    }
}

// Initialize taskpane when ONLYOFFICE is ready
window.Asc.plugin.init = function() {
    const simpleTaskpane = new SimpleTaskpane();
    simpleTaskpane.init().catch(console.error);
};

// Export for testing
export default SimpleTaskpane;
