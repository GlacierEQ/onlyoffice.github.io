/**
 * Word GPT Plus - Model Manager
 * Manages interactions with AI models and provides unified interface
 */

import simpleApiClient from './simple-api-client.js';

class ModelManager {
    constructor() {
        // Configuration
        this.config = {
            defaultModel: localStorage.getItem('wordGptPlusDefaultModel') || 'llama2',
            defaultSystemPrompt: 'You are a helpful AI assistant for Microsoft Word.',
            temperaturePresets: {
                creative: 0.9,
                balanced: 0.7,
                precise: 0.2
            },
            maxRetries: 2,
            timeout: 60000 // 60 seconds
        };

        // Cache for responses to reduce redundant API calls
        this.responseCache = new Map();
        this.cacheEnabled = localStorage.getItem('wordGptPlusCacheEnabled') !== 'false';
        this.maxCacheSize = 50;

        // Request tracking
        this.pendingRequests = new Map();
        this.requestHistory = [];

        // Statistics
        this.stats = {
            totalRequests: 0,
            successfulRequests: 0,
            failedRequests: 0,
            cacheHits: 0,
            averageResponseTime: 0
        };

        // Initialize
        this._loadStats();
    }

    /**
     * Generate text using AI model
     * @param {string} prompt - User prompt
     * @param {Object} options - Generation options
     * @returns {Promise<string>} Generated text
     */
    async generateText(prompt, options = {}) {
        const requestId = `req_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
        const startTime = performance.now();

        try {
            // Update stats
            this.stats.totalRequests++;

            // Prepare parameters
            const params = this._prepareParams(prompt, options);

            // Check cache if enabled
            if (this.cacheEnabled && !options.skipCache) {
                const cacheKey = this._generateCacheKey(prompt, params);
                const cachedResponse = this.responseCache.get(cacheKey);

                if (cachedResponse) {
                    this.stats.cacheHits++;
                    this._recordRequestCompletion(requestId, true, startTime);
                    return cachedResponse;
                }
            }

            // Track request
            this.pendingRequests.set(requestId, {
                prompt,
                options,
                startTime,
                status: 'processing'
            });

            // Process request through appropriate provider
            let response;

            // If running in demo mode with no API configured, use simulation
            if (options.demoMode || !simpleApiClient.hasValidConfig()) {
                response = await this._simulateResponse(prompt, params);
            } else {
                // Make actual API request
                response = await this._makeApiRequest(prompt, params);
            }

            // Cache the response if caching is enabled
            if (this.cacheEnabled && !options.skipCache) {
                const cacheKey = this._generateCacheKey(prompt, params);
                this._addToCache(cacheKey, response);
            }

            // Record successful completion
            this._recordRequestCompletion(requestId, true, startTime);

            return response;

        } catch (error) {
            // Record failure
            this._recordRequestCompletion(requestId, false, startTime, error);

            // Handle error
            console.error('Error generating text:', error);

            if (options.throwOnError) {
                throw error;
            } else {
                return `Error generating response: ${error.message}`;
            }
        }
    }

    /**
     * Generate embeddings for text
     * @param {string} text - Input text
     * @param {Object} options - Embedding options
     * @returns {Promise<number[]>} Text embedding vector
     */
    async generateEmbeddings(text, options = {}) {
        // In a full implementation, this would connect to an embeddings API
        // For now, provide a simplified simulation
        return this._simulateEmbeddings(text);
    }

    /**
     * Set the default model
     * @param {string} modelName - Model name
     */
    setDefaultModel(modelName) {
        this.config.defaultModel = modelName;
        localStorage.setItem('wordGptPlusDefaultModel', modelName);
    }

    /**
     * Enable or disable response caching
     * @param {boolean} enabled - Whether caching is enabled
     */
    setCaching(enabled) {
        this.cacheEnabled = enabled;
        localStorage.setItem('wordGptPlusCacheEnabled', enabled.toString());

        // Clear cache if disabling
        if (!enabled) {
            this.clearCache();
        }
    }

    /**
     * Clear the response cache
     */
    clearCache() {
        this.responseCache.clear();
    }

    /**
     * Get usage statistics
     * @returns {Object} Usage statistics
     */
    getStats() {
        return {
            ...this.stats,
            cacheSize: this.responseCache.size,
            pendingRequests: this.pendingRequests.size
        };
    }

    /**
     * Reset usage statistics
     */
    resetStats() {
        this.stats = {
            totalRequests: 0,
            successfulRequests: 0,
            failedRequests: 0,
            cacheHits: 0,
            averageResponseTime: 0
        };
        this._saveStats();
    }

    /**
     * Prepare parameters for API request
     * @private
     */
    _prepareParams(prompt, options) {
        // Start with defaults
        const params = {
            model: options.model || this.config.defaultModel,
            temperature: options.temperature !== undefined ? options.temperature : this.config.temperaturePresets.balanced,
            maxTokens: options.maxTokens || 1024,
            systemPrompt: options.systemPrompt || this.config.defaultSystemPrompt,
            detailed: options.detailed || false,
            format: options.format || 'text'
        };

        // If temperature is a named preset, resolve it
        if (typeof params.temperature === 'string' && this.config.temperaturePresets[params.temperature]) {
            params.temperature = this.config.temperaturePresets[params.temperature];
        }

        return params;
    }

    /**
     * Make API request to generate text
     * @private
     */
    async _makeApiRequest(prompt, params) {
        // In a real implementation, this would dynamically choose between different
        // API providers like OpenAI, Azure OpenAI, Anthropic, etc.
        return await simpleApiClient.generateText(prompt, params);
    }

    /**
     * Generate a cache key for a request
     * @private
     */
    _generateCacheKey(prompt, params) {
        const relevantParams = {
            model: params.model,
            temperature: params.temperature,
            systemPrompt: params.systemPrompt,
            detailed: params.detailed
        };

        return `${prompt}|${JSON.stringify(relevantParams)}`;
    }

    /**
     * Add response to cache
     * @private
     */
    _addToCache(key, value) {
        // Enforce cache size limit with LRU policy (remove oldest entries)
        if (this.responseCache.size >= this.maxCacheSize) {
            const oldestKey = this.responseCache.keys().next().value;
            this.responseCache.delete(oldestKey);
        }

        this.responseCache.set(key, value);
    }

    /**
     * Record request completion
     * @private
     */
    _recordRequestCompletion(requestId, success, startTime, error = null) {
        const elapsed = performance.now() - startTime;
        const requestInfo = this.pendingRequests.get(requestId) || {};

        // Update request status
        if (requestInfo) {
            requestInfo.status = success ? 'completed' : 'failed';
            requestInfo.elapsed = elapsed;
            if (error) requestInfo.error = error.message;
        }

        // Update stats
        if (success) {
            this.stats.successfulRequests++;
        } else {
            this.stats.failedRequests++;
        }

        // Update average response time
        const totalSuccessful = this.stats.successfulRequests;
        const currentAvg = this.stats.averageResponseTime;

        if (success) {
            this.stats.averageResponseTime =
                (currentAvg * (totalSuccessful - 1) + elapsed) / totalSuccessful;
        }

        // Save to history
        this.requestHistory.unshift({
            id: requestId,
            prompt: requestInfo.prompt?.substring(0, 100),
            success,
            elapsed,
            timestamp: new Date().toISOString(),
            error: error?.message
        });

        // Trim history to reasonable size
        if (this.requestHistory.length > 100) {
            this.requestHistory.length = 100;
        }

        // Remove from pending
        this.pendingRequests.delete(requestId);

        // Save stats
        this._saveStats();
    }

    /**
     * Save stats to localStorage
     * @private
     */
    _saveStats() {
        try {
            localStorage.setItem('wordGptPlusModelStats', JSON.stringify(this.stats));
        } catch (e) {
            console.warn('Failed to save model stats:', e);
        }
    }

    /**
     * Load stats from localStorage
     * @private
     */
    _loadStats() {
        try {
            const savedStats = localStorage.getItem('wordGptPlusModelStats');
            if (savedStats) {
                this.stats = { ...this.stats, ...JSON.parse(savedStats) };
            }
        } catch (e) {
            console.warn('Failed to load model stats:', e);
        }
    }

    /**
     * Simulate AI response for demo/testing
     * @private
     */
    async _simulateResponse(prompt, params) {
        // Add artificial delay to simulate network latency
        const delayMs = 1000 + Math.random() * 2000;
        await new Promise(resolve => setTimeout(resolve, delayMs));

        // Determine response type based on prompt content
        let responseType = 'general';

        if (prompt.toLowerCase().includes('summarize') || prompt.toLowerCase().includes('summary')) {
            responseType = 'summary';
        } else if (prompt.toLowerCase().includes('translate')) {
            responseType = 'translation';
        } else if (prompt.toLowerCase().includes('fix grammar') || prompt.toLowerCase().includes('grammar errors')) {
            responseType = 'grammarFix';
        } else if (prompt.toLowerCase().includes('outline')) {
            responseType = 'outline';
        }

        // Generate appropriate simulated response
        switch (responseType) {
            case 'summary':
                return this._generateSimulatedSummary(prompt);
            case 'translation':
                return this._generateSimulatedTranslation(prompt);
            case 'grammarFix':
                return this._generateSimulatedGrammarFix(prompt);
            case 'outline':
                return this._generateSimulatedOutline(prompt);
            default:
                return this._generateSimulatedGeneral(prompt, params);
        }
    }

    /**
     * Generate simulated text summary
     * @private
     */
    _generateSimulatedSummary(prompt) {
        return `This is a simulated summary generated by the Word GPT Plus offline mode. In a real implementation, this would analyze the input text and provide a concise summary focusing on the key points and maintaining the overall meaning and tone.

The summary would be approximately 25-30% of the original text length and would be designed to capture the essential information while removing redundant or less important details.`;
    }

    /**
     * Generate simulated translation
     * @private
     */
    _generateSimulatedTranslation(prompt) {
        const languages = {
            spanish: "Este es un texto traducido simulado. En una implementación real, esto sería una traducción precisa del texto original al español.",
            french: "Ceci est un texte traduit simulé. Dans une implémentation réelle, il s'agirait d'une traduction précise du texte original en français.",
            german: "Dies ist ein simulierter übersetzter Text. In einer realen Implementierung wäre dies eine genaue Übersetzung des Originaltextes ins Deutsche.",
            chinese: "这是一个模拟翻译的文本。在实际实现中，这将是原始文本的准确中文翻译。"
        };

        // Try to detect target language
        let targetLang = 'spanish'; // Default
        for (const lang of Object.keys(languages)) {
            if (prompt.toLowerCase().includes(lang)) {
                targetLang = lang;
                break;
            }
        }

        return languages[targetLang];
    }

    /**
     * Generate simulated grammar fix
     * @private
     */
    _generateSimulatedGrammarFix(prompt) {
        return `This is a simulated grammar correction. In a real implementation, this would fix grammar issues, spelling mistakes, punctuation errors, and improve sentence structure while maintaining the original meaning.

The corrections would be made with careful attention to context and would ensure proper subject-verb agreement, consistent tense usage, appropriate article usage, and correct word choice.`;
    }

    /**
     * Generate simulated outline
     * @private
     */
    _generateSimulatedOutline(prompt) {
        return `# Simulated Document Outline

I. Introduction
   A. Background information
   B. Thesis statement or main argument
   C. Overview of key points

II. First Main Section
   A. Key point 1
      1. Supporting evidence
      2. Examples
   B. Key point 2
      1. Supporting evidence
      2. Case studies

III. Second Main Section
   A. Analysis of findings
   B. Implications
      1. Short-term effects
      2. Long-term impacts

IV. Conclusion
   A. Restatement of main argument
   B. Summary of key points
   C. Call to action or final thoughts`;
    }

    /**
     * Generate simulated general response
     * @private
     */
    _generateSimulatedGeneral(prompt, params) {
        // Adjust response style based on temperature
        const temperature = params.temperature;
        let style = "balanced";

        if (temperature > 0.8) {
            style = "creative and varied";
        } else if (temperature < 0.4) {
            style = "precise and factual";
        }

        return `This is a simulated response from Word GPT Plus running in offline mode. 
        
I've analyzed your prompt: "${prompt.substring(0, 50)}${prompt.length > 50 ? '...' : ''}"

In a real implementation with an active AI model, you would receive a ${style} response that directly addresses your query or request. The response would be generated with a temperature setting of ${temperature.toFixed(1)}.

This simulation is provided to demonstrate the interface functionality. Connect to an AI model or API for actual content generation.`;
    }

    /**
     * Simulate text embeddings
     * @private
     */
    _simulateEmbeddings(text) {
        // Create a simple pseudo-embedding vector (not for real use)
        const vector = Array(128).fill(0).map(() => (Math.random() * 2) - 1);

        // Normalize the vector (ensure unit length)
        const magnitude = Math.sqrt(vector.reduce((sum, val) => sum + (val * val), 0));
        return vector.map(val => val / magnitude);
    }
}

// Export a singleton instance
const modelManager = new ModelManager();
export default modelManager;