/**
 * Word GPT Plus - Simple Configuration
 * Provides configuration for the simple taskpane UI
 */

const simpleConfig = {
    app: {
        name: 'Word GPT Plus (Free)',
        version: '0.5.0'
    },

    ai: {
        defaultModel: 'llama2',
        localEndpoint: 'http://localhost:11434/api',
        systemPrompts: {
            default: 'You are a helpful AI writing assistant. Your goal is to help the user improve their document by providing relevant, clear, and well-written responses. Be concise but thorough.',
            improve: 'You are a writing improvement expert. Your task is to enhance the given text by fixing grammar, improving clarity, and making it more engaging while maintaining the original meaning and tone. Provide the improved version only, without explanations.',
            summarize: 'You are a summarization specialist. Create a concise summary of the provided text that captures the key points and main message. The summary should be about 25% of the original length.',
            elaborate: 'You are a content expansion expert. Take the provided text and expand it with additional details, examples, and supporting points while maintaining the original message and tone.',
            translate: 'You are a professional translator. Translate the provided text accurately while preserving the meaning, tone, and style of the original content. Do not add or remove information.',
            explain: 'You are an expert at simplifying complex information. Explain the provided text using simple language that would be understandable to someone without specialized knowledge in the subject area.'
        },
        defaultParams: {
            temperature: 0.7,
            maxTokens: 1024,
            topP: 1,
            frequencyPenalty: 0,
            presencePenalty: 0
        }
    },

    ui: {
        templates: [
            {
                id: 'improve',
                name: 'Improve Writing',
                prompt: 'Please improve the following text to make it more professional and engaging:'
            },
            {
                id: 'summarize',
                name: 'Summarize',
                prompt: 'Please provide a concise summary of the following text:'
            },
            {
                id: 'elaborate',
                name: 'Elaborate',
                prompt: 'Please expand on the following text with additional details and examples:'
            },
            {
                id: 'translate',
                name: 'Translate',
                prompt: 'Please translate the following text to [language]:'
            },
            {
                id: 'explain',
                name: 'Explain Simply',
                prompt: 'Please explain the following text in simple terms that anyone can understand:'
            }
        ],
        theme: {
            primary: '#0078d4',
            secondary: '#2b88d8',
            accent: '#ffb900',
            background: '#ffffff',
            text: '#323130'
        }
    },

    settings: {
        saveHistory: true,
        autoSuggest: false,
        showWordCount: true,
        darkMode: false,
        fontSize: 14,

        loadFromStorage() {
            if (window.localStorage) {
                try {
                    const stored = localStorage.getItem('wordGptPlus_settings');
                    return stored ? JSON.parse(stored) : null;
                } catch (e) {
                    console.warn('Failed to load settings from localStorage');
                }
            }
            return null;
        },

        saveToStorage(settings) {
            if (window.localStorage) {
                try {
                    localStorage.setItem('wordGptPlus_settings', JSON.stringify(settings));
                    return true;
                } catch (e) {
                    console.warn('Failed to save settings to localStorage');
                }
            }
            return false;
        }
    }
};

export default simpleConfig;
