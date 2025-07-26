/**
 * Word GPT Plus - Simple Document Manager
 * Handles document interactions like getting selected text and inserting content
 */

class SimpleDocumentManager {
    constructor() {
        // Track document state
        this.documentContext = null;
        this.currentSelection = {
            text: '',
            range: null
        };
        this.documentStats = {
            wordCount: 0,
            paragraphCount: 0,
            characterCount: 0
        };
    }

    /**
     * Get currently selected text from Word document
     * @returns {Promise<string>} Selected text
     */
    async getSelectedText() {
        return new Promise((resolve, reject) => {
            try {
                window.Asc.plugin.executeMethod("GetSelectedText", null, function(text) {
                    resolve(text);
                });
            } catch (error) {
                console.error('Error getting selected text:', error);
                reject(error);
            }
        });
    }

    /**
     * Insert text into the document
     * @param {string} text - Text to insert
     * @returns {Promise<boolean>} Success indicator
     */
    async insertText(text) {
        return new Promise((resolve, reject) => {
            try {
                window.Asc.plugin.executeMethod("PasteText", [text], function() {
                    resolve(true);
                });
            } catch (error) {
                console.error('Error inserting text:', error);
                reject(error);
            }
        });
    }

    /**
     * Get document statistics
     * @returns {Promise<Object>} Document statistics
     */
    async getDocumentStats() {
        return new Promise((resolve, reject) => {
            try {
                window.Asc.plugin.executeMethod("GetAllContent", null, function(text) {
                    const wordCount = text.trim().split(/\s+/).length;
                    const characterCount = text.length;
                    // Note: Paragraph count is not directly available in the same way.
                    const paragraphCount = text.split(/\n+/).length;

                    this.documentStats = {
                        wordCount,
                        paragraphCount,
                        characterCount
                    };

                    resolve(this.documentStats);
                }.bind(this));
            } catch (error) {
                console.error('Error getting document stats:', error);
                reject(error);
            }
        });
    }
}

// Create and export singleton instance
const simpleDocumentManager = new SimpleDocumentManager();
export default simpleDocumentManager;
