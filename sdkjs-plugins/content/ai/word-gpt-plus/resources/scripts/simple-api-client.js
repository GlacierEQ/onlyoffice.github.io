/**
 * Word GPT Plus - Simple API Client
 * Handles API communication with local or remote AI models
 */

class SimpleApiClient {
    constructor() {
        this.localEndpoint = localStorage.getItem('wordGptPlusLocalEndpoint') || 'http://localhost:8080';
        this.model = localStorage.getItem('wordGptPlusLocalModel') || 'llama2-7b-q4';

        // Default configuration
        this.config = {
            useCache: true,
            retryCount: 3,
            timeout: 60000, // 60 seconds
        };
    }

    /**
     * Load configuration from storage
     */
    loadConfig() {
        try {
            const savedConfig = localStorage.getItem('wordGptPlusApiConfig');
            if (savedConfig) {
                const parsedConfig = JSON.parse(savedConfig);
                this.localEndpoint = parsedConfig.localEndpoint || this.localEndpoint;
                this.model = parsedConfig.model || this.model;

                // Merge additional config if present
                if (parsedConfig.config) {
                    this.config = { ...this.config, ...parsedConfig.config };
                }

                console.log('API configuration loaded');
            }
        } catch (error) {
            console.error('Error loading API configuration:', error);
        }
    }

    /**
     * Set local API configuration
     * @param {string} endpoint - Local API endpoint
     * @param {string} model - Model name
     */
    setLocalConfig(endpoint, model) {
        if (endpoint) this.localEndpoint = endpoint;
        if (model) this.model = model;

        // Save to storage
        localStorage.setItem('wordGptPlusLocalEndpoint', this.localEndpoint);
        localStorage.setItem('wordGptPlusLocalModel', this.model);

        // Save full config
        this.saveConfig();

        console.log('Local API configuration updated:', { endpoint: this.localEndpoint, model: this.model });
    }

    /**
     * Save current configuration to storage
     */
    saveConfig() {
        try {
            const config = {
                localEndpoint: this.localEndpoint,
                model: this.model,
                config: this.config
            };

            localStorage.setItem('wordGptPlusApiConfig', JSON.stringify(config));
        } catch (error) {
            console.error('Error saving API configuration:', error);
        }
    }

    /**
     * Check if configuration is valid
     * @returns {boolean} Is configuration valid
     */
    hasValidConfig() {
        return !!this.localEndpoint && !!this.model;
    }

    /**
     * Generate text using configured model
     * @param {string} prompt - Input prompt
     * @param {Object} options - Generation options
     * @returns {Promise<string>} Generated text
     */
    async generateText(prompt, options = {}) {
        if (!this.hasValidConfig()) {
            throw new Error('API not configured');
        }

        try {
            const requestBody = {
                prompt,
                model: options.model || this.model,
                temperature: options.temperature || 0.7,
                max_tokens: options.maxTokens || 2048,
                system_message: options.systemMessage || 'You are a helpful AI assistant.'
            };

            // For demonstration, we'll simulate the API call
            // In production, this would be replaced with an actual fetch call
            return this.simulateApiResponse(requestBody);
        } catch (error) {
            console.error('Text generation error:', error);
            throw error;
        }
    }

    /**
     * Simulate API response (for demo purposes)
     * @param {Object} request - Request parameters
     * @returns {Promise<string>} Simulated response
     * @private
     */
    async simulateApiResponse(request) {
        return new Promise((resolve) => {
            console.log('Simulating API call to:', this.localEndpoint);
            console.log('Request:', request);

            // Add a delay to simulate network latency
            setTimeout(() => {
                const responses = [
                    `I've analyzed your request regarding "${request.prompt.substring(0, 30)}..." and here's my response. This was generated using a local AI model running on your device, which means complete privacy and no data sent to external servers.`,

                    `Based on your prompt, I can provide the following insights. Remember that I'm running locally on your device, so my capabilities might be different from cloud-based models, but I offer enhanced privacy.`,

                    `Here's my response to your request. As a locally-running AI model, I process all data on your device without sending anything to external servers. This ensures your data remains private.`
                ];

                // Select a random response
                const response = responses[Math.floor(Math.random() * responses.length)];
                resolve(response);
            }, 2000); // Simulate 2-second processing time
        });
    }
}

// Create and export a singleton instance
const simpleApiClient = new SimpleApiClient();
export default simpleApiClient;
