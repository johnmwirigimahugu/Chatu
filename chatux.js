/**
 * farux.js - Frontend Integration Framework
 * Version: 1.0.0
 *
 * @Description: This framework combines the declarative power of tugs.js
 * with the versatile DOM manipulation and utility features of w3.js.
 * It provides a comprehensive, self-contained solution for building dynamic,
 * reactive, and interactive web interfaces directly from HTML, minimizing
 * complex JavaScript coding. All public APIs use the 'cx.' namespace,
 * and custom HTML attributes use the 'cx-' prefix.
 *
 * @InspiredBy: tugs.js ("Frontend Zen for Green Horns"), w3.js (DOM helpers)
 * @Author        : John Mwirigi Mahugu - "Kesh"
 * @Updated       : June 24, 2025
 * ============================================================================
 * Copyright (C) 2025 by John Mwirigi Mahugu
 * LICENSE {OPEN SOURCE}
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 * ============================================================================
 */

(function() {
    "use strict";

    // Define the global 'cx' object
    window.cx = window.cx || {};

    // --- Core Utilities (Derived from w3.js & Kesh.log/html) ---
    cx.dom = {
        /**
         * Selects the first element matching the CSS selector.
         * @param {string} selector - The CSS selector string.
         * @returns {HTMLElement|null} The first matching element or null.
         */
        get: function(selector) {
            return document.querySelector(selector);
        },
        /**
         * Selects all elements matching the CSS selector.
         * @param {string} selector - The CSS selector string.
         * @returns {NodeListOf<HTMLElement>} A NodeList of matching elements.
         */
        getAll: function(selector) {
            return document.querySelectorAll(selector);
        },
        /**
         * Hides an element by setting its display style to 'none'.
         * @param {string|HTMLElement} sel - CSS selector string or HTMLElement.
         */
        hide: function(sel) {
            const elements = (typeof sel === 'string') ? this.getAll(sel) : [sel];
            elements.forEach(el => { if (el) el.style.display = 'none'; });
        },
        /**
         * Shows an element by setting its display style to 'block'.
         * @param {string|HTMLElement} sel - CSS selector string or HTMLElement.
         */
        show: function(sel) {
            const elements = (typeof sel === 'string') ? this.getAll(sel) : [sel];
            elements.forEach(el => { if (el) el.style.display = 'block'; });
        },
        /**
         * Adds a CSS class to elements.
         * @param {string|HTMLElement} sel - CSS selector string or HTMLElement.
         * @param {string} cls - The class name to add.
         */
        addClass: function(sel, cls) {
            const elements = (typeof sel === 'string') ? this.getAll(sel) : [sel];
            elements.forEach(el => { if (el && el.classList) el.classList.add(cls); });
        },
        /**
         * Removes a CSS class from elements.
         * @param {string|HTMLElement} sel - CSS selector string or HTMLElement.
         * @param {string} cls - The class name to remove.
         */
        removeClass: function(sel, cls) {
            const elements = (typeof sel === 'string') ? this.getAll(sel) : [sel];
            elements.forEach(el => { if (el && el.classList) el.classList.remove(cls); });
        },
        /**
         * Toggles a CSS class on elements.
         * @param {string|HTMLElement} sel - CSS selector string or HTMLElement.
         * @param {string} cls - The class name to toggle.
         */
        toggleClass: function(sel, cls) {
            const elements = (typeof sel === 'string') ? this.getAll(sel) : [sel];
            elements.forEach(el => { if (el && el.classList) el.classList.toggle(cls); });
        },
        /**
         * Sets an inline style property for elements.
         * @param {string|HTMLElement} sel - CSS selector string or HTMLElement.
         * @param {string} prop - The CSS property name (e.g., 'background-color').
         * @param {string} val - The value to set.
         */
        style: function(sel, prop, val) {
            const elements = (typeof sel === 'string') ? this.getAll(sel) : [sel];
            elements.forEach(el => { if (el) el.style[prop] = val; });
        },
        /**
         * Attaches an event listener to elements.
         * @param {string|HTMLElement} sel - CSS selector string or HTMLElement.
         * @param {string} event - The event type (e.g., 'click', 'input').
         * @param {Function} handler - The event handler function.
         */
        on: function(sel, event, handler) {
            const elements = (typeof sel === 'string') ? this.getAll(sel) : [sel];
            elements.forEach(el => { if (el) el.addEventListener(event, handler); });
        },
        /**
         * Removes an event listener from elements.
         * @param {string|HTMLElement} sel - CSS selector string or HTMLElement.
         * @param {string} event - The event type.
         * @param {Function} handler - The handler function to remove.
         */
        off: function(sel, event, handler) {
            const elements = (typeof sel === 'string') ? this.getAll(sel) : [sel];
            elements.forEach(el => { if (el) el.removeEventListener(event, handler); });
        },
        /**
         * Performs a simple CSS animation.
         * @param {string|HTMLElement} sel - CSS selector string or HTMLElement.
         * @param {string} effect - The animation effect (conceptual, requires CSS transitions/keyframes).
         * @param {Function} [callback] - Callback after animation.
         */
        animate: function(sel, effect, callback) {
            const elements = (typeof sel === 'string') ? this.getAll(sel) : [sel];
            elements.forEach(el => {
                if (el) {
                    // This is a placeholder. Real animation would involve CSS classes/keyframes or JS animation engine.
                    console.warn(`[farux.js] Basic animate function for '${effect}' (conceptual). Requires CSS classes.`);
                    if (callback) setTimeout(callback, 500); // Simulate duration
                }
            });
        },
         /**
         * Replaces content inside an element.
         * @param {HTMLElement} element - The target element.
         * @param {string} search - String to search for.
         * @param {string} replace - String to replace with.
         */
        replaceHtml: function(element, search, replace) {
            if (element && element.innerHTML) {
                element.innerHTML = element.innerHTML.replace(new RegExp(search, 'g'), replace);
            }
        },
         /**
         * Simple templating utility. Replaces {{key}} with data[key].
         * @param {HTMLElement} templateElement - The template element.
         * @param {object} data - The data to populate.
         * @returns {HTMLElement} The populated clone.
         */
        template: function(templateElement, data) {
            if (!templateElement) return null;
            let clone = templateElement.cloneNode(true);
            if (!data) return clone;

            // Simplified replacement logic
            let html = clone.innerHTML;
            for (const key in data) {
                if (data.hasOwnProperty(key)) {
                    html = html.replace(new RegExp(`{{${key}}}`, 'g'), data[key]);
                }
            }
            clone.innerHTML = html;
            return clone;
        },
        /**
         * Includes HTML content from a URL into an element.
         * @param {string} url - The URL to fetch.
         * @param {string|HTMLElement} target - The target element or its selector.
         * @param {Function} [callback] - Callback after content is loaded.
         */
        includeHtml: async function(url, target, callback) {
            const targetElement = typeof target === 'string' ? cx.dom.get(target) : target;
            if (!targetElement) {
                console.error(`[farux.js] includeHtml: Target element not found for ${target}.`);
                return;
            }
            try {
                const response = await fetch(url);
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                targetElement.innerHTML = await response.text();
                if (callback) callback();
            } catch (error) {
                console.error(`[farux.js] includeHtml: Failed to load ${url}:`, error);
                targetElement.innerHTML = `<p style="color: red;">Error loading content from ${url}</p>`;
            }
        }
    };

    // --- AJAX & HTTP (Derived from ahah.js & w3.js get/postHttp) ---
    cx.ajax = {
        /**
         * Makes a GET request and inserts response into a target element.
         * @param {string} url - The URL to fetch.
         * @param {string|HTMLElement} target - The ID of the target element or the element itself.
         * @param {Function} [callback] - Optional callback after content is loaded.
         */
        loadHtml: async function(url, target, callback) {
            const targetElement = typeof target === 'string' ? cx.dom.get(target) : target;
            if (!targetElement) {
                console.error(`[farux.js] loadHtml: Target element for loadHtml not found:`, target);
                return;
            }
            targetElement.innerHTML = ' Fetching data...'; // Initial message
            try {
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const html = await response.text();
                targetElement.innerHTML = html;
                if (callback) callback();
            } catch (error) {
                targetElement.innerHTML = `[farux.js] AHAH Error:<br>${error.status || ''}<br>${error.message || error}`;
                console.error(`[farux.js] Error in loadHtml for ${url}:`, error);
            }
        },
        /**
         * Performs a generic HTTP GET request.
         * @param {string} url - The URL to request.
         * @param {Function} successCallback - Callback on success.
         * @param {Function} [errorCallback] - Callback on error.
         */
        get: async function(url, successCallback, errorCallback) {
            try {
                const response = await fetch(url);
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const data = await response.text(); // Return text, parse JSON if needed
                if (successCallback) successCallback(data);
            } catch (error) {
                if (errorCallback) errorCallback(error);
                console.error(`[farux.js] GET request failed to ${url}:`, error);
            }
        },
        /**
         * Performs a generic HTTP POST request.
         * @param {string} url - The URL to post to.
         * @param {any} data - Data to send.
         * @param {Function} successCallback - Callback on success.
         * @param {Function} [errorCallback] - Callback on error.
         * @param {string} [contentType='application/json'] - Content-Type header.
         */
        post: async function(url, data, successCallback, errorCallback, contentType = 'application/json') {
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': contentType },
                    body: (contentType === 'application/json') ? JSON.stringify(data) : data
                });
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const responseData = await response.text();
                if (successCallback) successCallback(responseData);
            } catch (error) {
                if (errorCallback) errorCallback(error);
                console.error(`[farux.js] POST request failed to ${url}:`, error);
            }
        }
    };

    // --- Global State & Logging (Derived from Kesh.store/log) ---
    cx.store = {
        _data: {},
        /**
         * Sets a value in the global store.
         * @param {string} k - The key.
         * @param {*} v - The value.
         */
        set: function(k, v) {
            this._data[k] = v;
            cx.log(`Store set: ${k} =`, v);
        },
        /**
         * Gets a value from the global store.
         * @param {string} k - The key.
         * @returns {*} The stored value.
         */
        get: function(k) {
            return this._data[k];
        }
    };

    /**
     * Simple logging utility.
     * @param {...*} args - Arguments to log.
     */
    cx.log = function(...args) {
        console.log('[farux.js]', ...args);
    };

    // --- Internationalization (Derived from Kesh.lang) ---
    cx.lang = {
        _translations: {},
        _locale: 'en',
        /**
         * Sets translations for a locale.
         * @param {object} translations - An object where keys are locales (e.g., 'en', 'es')
         * and values are translation objects.
         */
        setTranslations: function(translations) {
            Object.assign(this._translations, translations);
            cx.log('Translations loaded:', translations);
        },
        /**
         * Sets the current locale.
         * @param {string} locale - The locale code (e.g., 'en', 'es').
         */
        setLocale: function(locale) {
            this._locale = locale;
            cx.log('Locale set to:', locale);
        },
        /**
         * Translates a key, optionally with parameters.
         * @param {string} key - The translation key.
         * @param {object} [params={}] - Parameters for substitution (e.g., {name: 'World'}).
         * @returns {string} The translated string.
         */
        get: function(key, params = {}) {
            let translation = (this._translations[this._locale] && this._translations[this._locale][key]) || key;
            for (const param in params) {
                translation = translation.replace(new RegExp(`{${param}}`, 'g'), params[param]);
            }
            return translation;
        }
    };

    // --- HTML Helpers (Derived from Kesh.html) ---
    cx.html = {
        /**
         * Escapes HTML entities in a string to prevent XSS.
         * @param {string} str - The string to escape.
         * @returns {string} The escaped string.
         */
        escape: function(str) {
            if (typeof str !== 'string') return str;
            const div = document.createElement('div');
            div.appendChild(document.createTextNode(str));
            return div.innerHTML;
        },
        /**
         * Strips HTML tags from a string.
         * @param {string} html - The HTML string.
         * @returns {string} The text content.
         */
        stripTags: function(html) {
            if (typeof html !== 'string') return html;
            const div = document.createElement('div');
            div.innerHTML = html;
            return div.textContent || div.innerText || "";
        },
        /**
         * Converts plain text newlines to <br> tags.
         * @param {string} text - The text string.
         * @returns {string} Text with <br> tags.
         */
        nl2br: function(text) {
            if (typeof text !== 'string') return text;
            return text.replace(/\n/g, '<br>');
        }
    };

    // --- Utility Checks (Derived from w3.js) ---
    cx.utils = {
        /**
         * Checks if a value is an array.
         * @param {*} arr - The value to check.
         * @returns {boolean} True if it's an array, false otherwise.
         */
        isArray: function(arr) {
            return typeof arr === "object" && arr.constructor === Array;
        },
        /**
         * Checks if a value is an object.
         * @param {*} obj - The value to check.
         * @returns {boolean} True if it's an object, false otherwise.
         */
        isObject: function(obj) {
            return typeof obj === "object" && obj.constructor === Object;
        },
        /**
         * Checks if a value is NaN.
         * @param {*} x - The value to check.
         * @returns {boolean} True if it's NaN, false otherwise.
         */
        isNaN: function(x) {
            return x === "" || (x / 1).toString() === "NaN";
        },
        /**
         * Trims whitespace from a string.
         * @param {string} x - The string to trim.
         * @returns {string} The trimmed string.
         */
        trim: function(x) {
            return x.replace(/^\s+|\s+$/gm, '');
        }
    };


    // --- Reactivity & Attributes (Derived from tugs.js kx-data, kx-bind etc.) ---
    const reactivity = {
        _proxies: new WeakMap(), // To store Kx data proxies
        _watchers: new WeakMap(), // To store watchers for elements
        _proxyTraps: {
            set(target, prop, value) {
                const oldVal = target[prop];
                target[prop] = value;
                if (oldVal !== value) {
                    // Trigger updates for elements bound to this prop
                    reactivity._updateBoundElements(target, prop, value);
                }
                return true;
            },
            get(target, prop) {
                // Return proxy for nested objects
                if (cx.utils.isObject(target[prop]) || cx.utils.isArray(target[prop])) {
                    if (!reactivity._proxies.has(target[prop])) {
                        reactivity._proxies.set(target[prop], new Proxy(target[prop], reactivity._proxyTraps));
                    }
                    return reactivity._proxies.get(target[prop]);
                }
                return target[prop];
            }
        },

        _updateBoundElements: function(targetProxy, prop, value) {
            // Find all elements that had this proxy attached and need updating for this prop
            cx.dom.getAll(`[cx-bind="${prop}"], [cx-text="${prop}"], [cx-show="${prop}"]`).forEach(el => {
                const dataScope = reactivity._proxies.get(el.__cx_data_original) || el.__cx_data_original;
                if (dataScope && dataScope === targetProxy) { // Ensure it's the correct data scope
                    if (el.hasAttribute(`cx-bind`) && el.getAttribute('cx-bind') === prop) {
                        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.tagName === 'SELECT') {
                            if (el.value !== value) el.value = value;
                        }
                    }
                    if (el.hasAttribute(`cx-text`) && el.getAttribute('cx-text') === prop) {
                        el.innerText = value;
                    }
                    if (el.hasAttribute(`cx-show`) && el.getAttribute('cx-show') === prop) {
                        if (value) cx.dom.show(el); else cx.dom.hide(el);
                    }
                }
            });

            // Also check for {{prop}} in innerHTML
            cx.dom.getAll('[cx-data]').forEach(el => {
                const dataRaw = el.__cx_data_original;
                if (dataRaw && reactivity._proxies.has(dataRaw)) {
                    // This is a simpler check, could be optimized for specific bindings
                    if (el.innerHTML.includes(`{{${prop}}}`)) {
                        reactivity._applyTextBindings(el, reactivity._proxies.get(dataRaw));
                    }
                }
            });
        },

        _applyTextBindings: function(element, dataProxy) {
            let originalHTML = element.getAttribute('data-cx-original-html');
            if (!originalHTML) {
                originalHTML = element.innerHTML;
                element.setAttribute('data-cx-original-html', originalHTML);
            }

            let newHTML = originalHTML;
            const matches = originalHTML.match(/\{\{([a-zA-Z0-9_.]+)\}\}/g);
            if (matches) {
                matches.forEach(match => {
                    const propPath = match.substring(2, match.length - 2); // e.g., "user.name"
                    let value = dataProxy;
                    try {
                        propPath.split('.').forEach(p => {
                            if (value !== null && typeof value === 'object' && value.hasOwnProperty(p)) {
                                value = value[p];
                            } else {
                                value = undefined; // Path not found
                                throw new Error('Path not found'); // Break loop
                            }
                        });
                    } catch (e) {
                        value = ''; // Set to empty string if path not found
                    }
                    newHTML = newHTML.replace(new RegExp(match.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'), 'g'), cx.html.escape(value === undefined ? '' : value));
                });
            }
            element.innerHTML = newHTML;
        },

        _initDataScope: function(element) {
            let dataAttr = element.getAttribute('cx-data');
            if (dataAttr) {
                let data = {};
                try {
                    data = JSON.parse(dataAttr);
                } catch (e) {
                    cx.log('Error parsing cx-data JSON:', e);
                }

                // Handle cx-persist
                const persistKey = element.getAttribute('cx-persist');
                if (persistKey) {
                    const persistedData = sessionStorage.getItem(persistKey);
                    if (persistedData) {
                        try {
                            const parsedPersisted = JSON.parse(persistedData);
                            // Merge persisted data, giving preference to persisted values
                            data = { ...data, ...parsedPersisted };
                        } catch (e) {
                            cx.log('Error parsing cx-persist data:', e);
                        }
                    }
                    // Save data to session storage on changes (proxied set handler will trigger this)
                    const originalSetTrap = reactivity._proxyTraps.set;
                    reactivity._proxyTraps.set = function(target, prop, value) {
                        const result = originalSetTrap.apply(this, arguments);
                        sessionStorage.setItem(persistKey, JSON.stringify(target));
                        return result;
                    };
                }

                // Create proxy and attach to element (raw data also attached for persistence)
                const dataProxy = new Proxy(data, reactivity._proxyTraps);
                element.kx = dataProxy; // Publicly expose as .kx on the element
                element.__cx_data_original = data; // Keep reference to original data for proxy traps

                // Initial render for bindings
                cx.dom.getAll('[cx-bind], [cx-text], [cx-show]', element).forEach(child => {
                    const bindProp = child.getAttribute('cx-bind');
                    const textProp = child.getAttribute('cx-text');
                    const showProp = child.getAttribute('cx-show');

                    if (bindProp) {
                        if (child.tagName === 'INPUT' || child.tagName === 'TEXTAREA' || child.tagName === 'SELECT') {
                            child.value = dataProxy[bindProp] || '';
                            cx.dom.on(child, 'input', (e) => {
                                dataProxy[bindProp] = e.target.value;
                            });
                        }
                    }
                    if (textProp) {
                        child.innerText = dataProxy[textProp] || '';
                    }
                    if (showProp) {
                        if (dataProxy[showProp]) cx.dom.show(child); else cx.dom.hide(child);
                    }
                });
                 reactivity._applyTextBindings(element, dataProxy);
            }
        },

        _initClickEvents: function(element) {
            const clickAttr = element.getAttribute('@click');
            if (clickAttr) {
                cx.dom.on(element, 'click', (event) => {
                    try {
                        // Create a context for the eval, including 'event' and 'kx' if available
                        const cxContext = element.closest('[cx-data]');
                        const kx = cxContext ? cxContext.kx : {}; // Use kx from closest cx-data
                        new Function('event', 'kx', clickAttr)(event, kx);
                    } catch (e) {
                        cx.log('Error in @click handler:', e);
                    }
                });
            }
        }
    };


    // --- Core Framework Init (Derived from tugs.js main loop) ---
    cx.init = function() {
        cx.log('farux.js initialized.');

        // Initialize components
        cx.dom.getAll('template[cx-component]').forEach(tpl => {
            const componentName = tpl.getAttribute('cx-component');
            cx.store.set(`__component__${componentName}`, tpl.innerHTML);
            tpl.remove(); // Remove template from DOM
        });

        cx.dom.getAll('[cx-use]').forEach(el => {
            const componentName = el.getAttribute('cx-use');
            const componentHtml = cx.store.get(`__component__${componentName}`);
            if (componentHtml) {
                el.innerHTML = componentHtml;
            } else {
                cx.log(`Component '${componentName}' not found.`);
            }
        });

        // Initialize reactivity
        cx.dom.getAll('[cx-data]').forEach(el => {
            reactivity._initDataScope(el);
        });

        // Initialize click handlers
        cx.dom.getAll('[cx-data] [@click], :not([cx-data]) [@click]').forEach(el => {
             reactivity._initClickEvents(el);
        });

        // Initialize RESTful attributes (cx-get, cx-post, etc.)
        const restMethods = ['get', 'post', 'put', 'patch', 'delete'];
        restMethods.forEach(method => {
            cx.dom.getAll(`[cx-${method}]`).forEach(el => {
                cx.dom.on(el, 'click', async (e) => {
                    e.preventDefault();
                    const url = el.getAttribute(`cx-${method}`);
                    const targetSelector = el.getAttribute('cx-swap');
                    const transition = el.getAttribute('cx-transition');
                    const data = el.getAttribute('cx-data-payload'); // Optional payload for POST/PUT etc.

                    const targetElement = targetSelector ? cx.dom.get(targetSelector) : null;

                    if (url) {
                        let requestData = null;
                        if (data) {
                            try {
                                requestData = JSON.parse(data);
                            } catch (error) {
                                cx.log('Error parsing cx-data-payload JSON:', error);
                            }
                        } else if (el.tagName === 'FORM' && method === 'post') {
                            requestData = new FormData(el); // For form submissions
                        }

                        // Use cx.ajax for requests
                        const successCallback = (responseHtml) => {
                            if (targetElement) {
                                if (transition === 'fade') {
                                    cx.dom.addClass(targetElement, 'cx-fade-out'); // Assume CSS for fade out
                                    setTimeout(() => {
                                        targetElement.innerHTML = responseHtml;
                                        cx.dom.removeClass(targetElement, 'cx-fade-out');
                                        cx.dom.addClass(targetElement, 'cx-fade-in'); // Assume CSS for fade in
                                        setTimeout(() => cx.dom.removeClass(targetElement, 'cx-fade-in'), 500);
                                    }, 500);
                                } else if (transition === 'slide-left') {
                                    cx.dom.addClass(targetElement, 'cx-slide-left-out');
                                    setTimeout(() => {
                                        targetElement.innerHTML = responseHtml;
                                        cx.dom.removeClass(targetElement, 'cx-slide-left-out');
                                        cx.dom.addClass(targetElement, 'cx-slide-left-in');
                                        setTimeout(() => cx.dom.removeClass(targetElement, 'cx-slide-left-in'), 500);
                                    }, 500);
                                }
                                else {
                                    targetElement.innerHTML = responseHtml;
                                }
                            }
                        };
                        const errorCallback = (error) => {
                             if (targetElement) {
                                targetElement.innerHTML = `<p style="color: red;">Error: ${error.message || 'Failed to load content.'}</p>`;
                            }
                            cx.log(`AJAX ${method.toUpperCase()} request failed for ${url}:`, error);
                        };

                        if (method === 'get') {
                            await cx.ajax.get(url, successCallback, errorCallback);
                        } else {
                            await cx.ajax.post(url, requestData, successCallback, errorCallback, (requestData instanceof FormData) ? 'application/x-www-form-urlencoded' : 'application/json');
                        }
                    }
                });
            });
        });

        // Initialize Routing (cx-route, cx-view)
        cx.dom.getAll('[cx-route]').forEach(link => {
            cx.dom.on(link, 'click', e => {
                e.preventDefault();
                const targetView = cx.dom.get('[cx-view]');
                if (!targetView) {
                    cx.log('No [cx-view] element found for routing.');
                    return;
                }
                const href = link.getAttribute('href') || link.getAttribute('cx-route');
                if (href) {
                    cx.ajax.loadHtml(href, targetView, () => {
                        history.pushState({}, '', href);
                        cx.log(`Navigated to: ${href}`);
                    });
                }
            });
        });

        // Handle browser popstate for back/forward buttons
        window.addEventListener('popstate', () => {
            const targetView = cx.dom.get('[cx-view]');
            if (targetView) {
                cx.ajax.loadHtml(location.pathname, targetView, () => {
                    cx.log(`Popstate navigated to: ${location.pathname}`);
                });
            }
        });

        // Initialize Long Polling (cx-poll)
        cx.dom.getAll('[cx-poll]').forEach(el => {
            const url = el.getAttribute('cx-poll');
            const targetSelector = el.getAttribute('cx-swap') || el.id; // Use element itself if no swap target
            const interval = parseInt(el.getAttribute('cx-poll-interval') || '3000', 10); // Default 3 seconds

            if (url && targetSelector) {
                const poll = async () => {
                    await cx.ajax.loadHtml(url, targetSelector);
                    setTimeout(poll, interval);
                };
                cx.log(`Starting long polling for ${url} every ${interval}ms.`);
                poll(); // Initial poll
            }
        });

        // Initialize Form Validation (cx-validate)
        cx.dom.getAll('form[cx-validate]').forEach(form => {
            cx.dom.on(form, 'submit', e => {
                let isValid = true;
                // Basic HTML5 validation check
                form.querySelectorAll('[required]').forEach(input => {
                    if (!input.value.trim()) {
                        isValid = false;
                        input.style.border = '1px solid red'; // Simple visual feedback
                        cx.log(`Validation: ${input.id} is required.`);
                    } else {
                        input.style.border = '';
                    }
                });

                if (!isValid) {
                    e.preventDefault(); // Prevent submission if invalid
                    cx.log('Form validation failed!');
                    // In a real app, show cx.flash error or specific message
                } else {
                    cx.log('Form validation passed (conceptually).');
                    // Actual form submission would occur if no e.preventDefault() here
                    // or handle form submission via cx.ajax.post etc.
                }
            });
        });

        // Initialize Flash Messaging (cx-flash)
        cx.dom.flash = { // Add flash to cx.dom for easy access
            _messages: [],
            _displayArea: cx.dom.get('[cx-flash]'),
            /**
             * Displays a flash message.
             * @param {string} type - 'success', 'error', 'info'.
             * @param {string} message - The message text.
             */
            add: function(type, message) {
                this._messages.push({ type, message });
                this._render();
            },
            _render: function() {
                if (!this._displayArea) return;
                const msg = this._messages.shift();
                if (msg) {
                    const msgEl = document.createElement('div');
                    msgEl.className = `cx-flash-message cx-flash-${msg.type}`;
                    msgEl.innerText = msg.message;
                    this._displayArea.innerHTML = ''; // Clear previous
                    this._displayArea.appendChild(msgEl);
                    cx.dom.show(this._displayArea);

                    setTimeout(() => {
                        cx.dom.hide(this._displayArea);
                        msgEl.remove();
                        if (this._messages.length > 0) {
                            this._render(); // Show next message if any
                        }
                    }, 3000); // Hide after 3 seconds
                }
            }
        };
// 🌐 cx-include: Automatically loads external HTML into an element by kesh
// 🌐 cx-include: Load external HTML into an element (supports nesting + callback)
// Usage:
// <div cx-include="menu.html" cx-oninclude="initSidebar()"></div>

document.addEventListener("DOMContentLoaded", () => {
  const included = new Set();

  function loadIncludes(scope = document) {
    const elements = scope.querySelectorAll("[cx-include]");
    elements.forEach(el => {
      const file = el.getAttribute("cx-include");
      const callback = el.getAttribute("cx-oninclude");
      if (!file) return;

      // Avoid re-including same file
      if (included.has(el)) return;

      fetch(file)
        .then(res => {
          if (!res.ok) throw new Error(`Failed to load ${file}`);
          return res.text();
        })
        .then(html => {
          el.innerHTML = html;
          included.add(el);

          // Recursively scan for inner includes
          loadIncludes(el);

          // If a callback is provided
          if (callback && typeof window[callback.split("(")[0]] === "function") {
            try {
              new Function(callback)();
            } catch (e) {
              console.warn("cx-oninclude error:", e);
            }
          }
        })
        .catch(err => {
          console.error("cx-include error:", err);
          el.innerHTML = "<!-- cx-include failed -->";
        });
    });
  }

  loadIncludes();
});
/** EOF- End of Framework */
/* 🧪 Example Usage
html
Copy
Edit
<!-- Basic include -->
<div cx-include="menu.html"></div>

<!-- Include with callback -->
<div cx-include="sidebar.html" cx-oninclude="initSidebar()"></div>

<!-- Nested example: dashboard.html contains more <div cx-include="..."> inside -->
<div cx-include="dashboard.html"></div>
        // Rebind Kesh.flash to cx.dom.flash.add
        window.alert = function(message) { // Replace alert with custom message
            cx.dom.flash.add('info', message);
        };
    };


    // Auto-initialize farux.js when the DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', cx.init);
    } else {
        cx.init();
    }

}());
/** farux.js example page tugs+w3.js InspiredBy
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>farux.js Demonstration</title>
    <style>
        body { font-family: 'Inter', sans-serif; margin: 20px; background-color: #f0f4f8; color: #2c3e50; }
        .container { max-width: 900px; margin: 20px auto; background-color: #ffffff; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); }
        h1, h2 { color: #34495e; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; margin-top: 30px; }
        button {
            background-color: #3498db; color: white; padding: 12px 20px; border: none;
            border-radius: 8px; cursor: pointer; font-size: 16px; margin: 8px 5px;
            transition: background-color 0.3s ease, transform 0.2s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        button:hover { background-color: #2980b9; transform: translateY(-2px); }
        button:active { transform: translateY(0); box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }
        input[type="text"], input[type="email"] {
            padding: 10px; border: 1px solid #c0d9eb; border-radius: 6px; margin-bottom: 15px;
            width: calc(100% - 22px); box-sizing: border-box; font-size: 16px;
        }
        input:focus { outline: none; border-color: #3498db; box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2); }

        /* farux.js Layout System */
        [cx-row] { display: flex; flex-wrap: wrap; margin: -10px; }
        [cx-row] > [cx-col-1], [cx-row] > [cx-col-2], [cx-row] > [cx-col-3], [cx-row] > [cx-col-4],
        [cx-row] > [cx-col-5], [cx-row] > [cx-col-6], [cx-row] > [cx-col-7], [cx-row] > [cx-col-8],
        [cx-row] > [cx-col-9], [cx-row] > [cx-col-10], [cx-row] > [cx-col-11], [cx-row] > [cx-col-12] {
            padding: 10px; box-sizing: border-box;
        }
        [cx-col-1] { width: 8.33%; } [cx-col-2] { width: 16.66%; } [cx-col-3] { width: 25%; }
        [cx-col-4] { width: 33.33%; } [cx-col-5] { width: 41.66%; } [cx-col-6] { width: 50%; }
        [cx-col-7] { width: 58.33%; } [cx-col-8] { width: 66.66%; } [cx-col-9] { width: 75%; }
        [cx-col-10] { width: 83.33%; } [cx-col-11] { width: 91.66%; } [cx-col-12] { width: 100%; }

        /* farux.js Transition styles */
        .cx-fade-out { opacity: 1; transition: opacity 0.5s ease-out; }
        .cx-fade-out.active { opacity: 0; }
        .cx-fade-in { opacity: 0; transition: opacity 0.5s ease-in; }
        .cx-fade-in.active { opacity: 1; }
        .cx-slide-left-out { transform: translateX(0); transition: transform 0.5s ease-out; }
        .cx-slide-left-out.active { transform: translateX(-100%); }
        .cx-slide-left-in { transform: translateX(100%); transition: transform 0.5s ease-in; }
        .cx-slide-left-in.active { transform: translateX(0); }

        /* Flash message styles */
        .cx-flash-message {
            padding: 12px 20px; border-radius: 8px; margin-bottom: 15px;
            font-weight: bold; color: white; opacity: 0; transition: opacity 0.3s ease-in-out;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        .cx-flash-message.show { opacity: 1; }
        .cx-flash-success { background-color: #2ecc71; }
        .cx-flash-error { background-color: #e74c3c; }
        .cx-flash-info { background-color: #3498db; }
        #flash-message-area { min-height: 40px; margin-top: 20px;} /* Ensure space for flashes */

        /* Conditional display (cx-show) */
        [cx-show] { display: none; }
        [cx-show][data-cx-visible="true"] { display: block; }
    </style>
    <!-- Include farux.js here -->
    <!-- In a real scenario, this would be a single file compiled by your build process -->
    <script src="farux.js"></script>
</head>
<body>
    <div class="container">
        <h1>farux.js Core Features Demonstration</h1>

        <h2>1. Global State (`cx.store`)</h2>
        <p>Manage simple global key-value pairs and observe changes.</p>
        <div id="global-store-output" style="background-color: #ecf0f1; padding: 10px; border-radius: 6px; margin-bottom: 10px;">
            App Name: <span id="app-name-display">Not Set</span>
        </div>
        <button onclick="cx.store.set('appName', 'farux.js App'); updateGlobalStoreDisplay();">Set App Name</button>
        <button onclick="cx.log('Current App Name:', cx.store.get('appName'));">Log App Name</button>
        <script>
            function updateGlobalStoreDisplay() {
                document.getElementById('app-name-display').innerText = cx.store.get('appName') || 'Not Set';
            }
            document.addEventListener('DOMContentLoaded', updateGlobalStoreDisplay);
        </script>

        <h2>2. RESTful Verbs & Content Swapping (`cx-get`, `cx-swap`, `cx-transition`)</h2>
        <p>Load content from simulated API endpoints with visual transitions.</p>
        <button cx-get="/api/dynamic-content" cx-swap="#content-area" cx-transition="fade-out">Load Dynamic Content (Fade)</button>
        <button cx-get="/api/another-content" cx-swap="#content-area" cx-transition="slide-left-out">Load Another Content (Slide)</button>
        <div id="content-area" style="border: 1px dashed #b1c7d8; padding: 20px; min-height: 120px; margin-top: 15px; background-color: #eaf2f8; border-radius: 8px;">
            <h3>Welcome to the Content Area!</h3>
            <p>This content will be dynamically replaced by AJAX requests triggered by the buttons above.</p>
        </div>

        <h2>3. Component System (`<template cx-component>`, `<div cx-use>`)</h2>
        <p>Define reusable HTML components and inject them with `cx-use`.</p>

        <template cx-component="user-card">
            <div style="border: 1px solid #2ecc71; padding: 15px; margin-bottom: 10px; border-radius: 8px; background-color: #e9f7ee; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                <h4>Welcome, <span cx-text="name"></span>!</h4>
                <p>Email: <span cx-text="email"></span></p>
                <p>This is a reusable component powered by farux.js.</p>
                <button @click="alert('Hello from ' + kx.name + '!');">Say Hello</button>
            </div>
        </template>

        <div cx-use="user-card" cx-data='{ "name": "Alice Wonderland", "email": "alice@example.com" }'></div>
        <div cx-use="user-card" cx-data='{ "name": "Bob The Builder", "email": "bob@example.com" }'></div>

        <h2>4. Reactivity (`cx-data`, `cx-persist`, `cx-bind`, `cx-show`, `cx-text`)</h2>
        <p>Live data binding and conditional display for interactive forms.</p>

        <div cx-data='{ "userName": "Guest", "isWelcomeVisible": true, "favoriteColor": "#3498db" }' cx-persist="faruxFormData"
             style="background-color: #f7f9fc; padding: 20px; border-radius: 10px; margin-top: 20px;">
            <label for="userNameInput" style="display: block; margin-bottom: 8px; font-weight: bold;">Your Name:</label>
            <input type="text" id="userNameInput" cx-bind="userName" placeholder="Enter your name">
            <p>Hello, <span cx-text="userName"></span>!</p>

            <label for="colorPicker" style="display: block; margin-top: 15px; margin-bottom: 8px; font-weight: bold;">Favorite Color:</label>
            <input type="color" id="colorPicker" cx-bind="favoriteColor" style="display: block; width: 100px; height: 40px; border: none; padding: 0;">
            <p style="margin-top: 10px;">Selected color: <span cx-text="favoriteColor"></span></p>
            <div style="width: 50px; height: 50px; border-radius: 50%; display: inline-block; vertical-align: middle; margin-left: 10px;"
                 cx-bind="style.backgroundColor:favoriteColor"></div>

            <button @click="kx.isWelcomeVisible = !kx.isWelcomeVisible;" style="margin-top: 20px;">Toggle Welcome Message</button>
            <p cx-show="isWelcomeVisible" style="background-color: #d1ecf1; padding: 10px; border-left: 5px solid #29b6f6; border-radius: 4px; margin-top: 15px;">
                This message toggles visibility based on `isWelcomeVisible`.
            </p>
            <p style="font-size: 0.9em; color: #7f8c8d; margin-top: 15px;">
                Try changing input and refreshing the page; `cx-persist` will save your data!
            </p>
        </div>

        <h2>5. Event Handling (`@click`)</h2>
        <p>Execute JavaScript directly on click events.</p>
        <button @click="cx.log('You clicked the event handler button!'); alert('Event handler activated!');">Trigger Event</button>

        <h2>6. Layout System (`cx-row`, `cx-col-N`)</h2>
        <p>Responsive grid layout for structured content.</p>
        <div cx-row style="border: 1px dashed #a0d4b1; padding: 10px; background-color: #f0f7f2; border-radius: 8px;">
            <div cx-col-4 style="background-color: #d4edda; padding: 15px; border-radius: 6px;">Column A (4/12)</div>
            <div cx-col-4 style="background-color: #c3e6cb; padding: 15px; border-radius: 6px;">Column B (4/12)</div>
            <div cx-col-4 style="background-color: #b3dfc9; padding: 15px; border-radius: 6px;">Column C (4/12)</div>
        </div>
        <div cx-row style="border: 1px dashed #d1c6e0; padding: 10px; margin-top: 15px; background-color: #f5f3f8; border-radius: 8px;">
            <div cx-col-6 style="background-color: #e0d7ed; padding: 15px; border-radius: 6px;">Half Width</div>
            <div cx-col-6 style="background-color: #cfc2e1; padding: 15px; border-radius: 6px;">Other Half</div>
        </div>

        <h2>7. Routing (`cx-route`, `cx-view`)</h2>
        <p>Client-side routing for SPA experience.</p>
        <nav style="margin-top: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
            <a cx-route="/pages/home.html" href="/pages/home.html" style="margin-right: 20px; text-decoration: none; color: #3498db; font-weight: bold;">Home</a>
            <a cx-route="/pages/about.html" href="/pages/about.html" style="margin-right: 20px; text-decoration: none; color: #3498db; font-weight: bold;">About Us</a>
            <a cx-route="/pages/contact.html" href="/pages/contact.html" style="text-decoration: none; color: #3498db; font-weight: bold;">Contact</a>
        </nav>
        <div cx-view style="border: 1px solid #aeb6bf; padding: 20px; min-height: 150px; margin-top: 15px; background-color: #fbfcfc; border-radius: 8px;">
            <!-- Dynamic content for routes will load here -->
            <p>Navigate using the links above. Content will load here without a full page refresh.</p>
            <p>Current Path: <span id="current-route-path">/</span></p>
        </div>
        <script>
            // Update current path display
            window.addEventListener('popstate', () => {
                document.getElementById('current-route-path').innerText = location.pathname;
            });
            document.addEventListener('DOMContentLoaded', () => {
                document.getElementById('current-route-path').innerText = location.pathname;
            });
        </script>

        <h2>8. Form Validation (`cx-validate`)</h2>
        <p>Basic client-side validation on form submission.</p>
        <form cx-validate @submit="alert('Form submission initiated! Check console for validation logs.');"
              style="background-color: #ffeccf; padding: 20px; border-radius: 10px; margin-top: 20px;">
            <label for="requiredName" style="display: block; margin-bottom: 8px;">Your Name (Required):</label>
            <input type="text" id="requiredName" required placeholder="Enter your name" style="margin-bottom: 15px;">

            <label for="requiredEmail" style="display: block; margin-bottom: 8px;">Your Email (Required, Email format):</label>
            <input type="email" id="requiredEmail" required placeholder="Enter your email" style="margin-bottom: 15px;">

            <button type="submit">Submit Form</button>
            <p style="font-size: 0.9em; color: #7f8c8d; margin-top: 15px;">
                Try submitting with empty/invalid fields. Conceptual validation is logged to console.
            </p>
        </form>

        <h2>9. Flash Messaging (`cx-flash`)</h2>
        <p>Display temporary, non-blocking notification messages.</p>
        <div id="flash-message-area" cx-flash style="background-color: #ecf0f1; padding: 10px; border-radius: 6px;">
            <!-- Flash messages will appear here -->
        </div>
        <button onclick="cx.dom.flash.add('success', 'User data saved successfully!');">Show Success</button>
        <button onclick="cx.dom.flash.add('error', 'Failed to connect to server!');">Show Error</button>
        <button onclick="cx.dom.flash.add('info', 'New update available.');">Show Info</button>

        <h2>10. Internationalization (`cx.lang`)</h2>
        <p>Simple text translation with parameter substitution.</p>
        <script>
            cx.lang.setTranslations({
                "en": { "greeting": "Hello, {user}!", "welcome": "Welcome to farux.js!" },
                "es": { "greeting": "¡Hola, {user}!", "welcome": "¡Bienvenido a farux.js!" }
            });
            cx.lang.setLocale("en"); // Default locale
        </script>
        <p style="background-color: #e8f5e9; padding: 10px; border-radius: 6px; margin-top: 15px;">
            <span id="lang-greeting"></span> <span id="lang-welcome"></span>
        </p>
        <button onclick="cx.lang.setLocale('es'); updateLangDisplay();">Switch to Spanish</button>
        <button onclick="cx.lang.setLocale('en'); updateLangDisplay();">Switch to English</button>
        <script>
            function updateLangDisplay() {
                document.getElementById('lang-greeting').innerText = cx.lang.get('greeting', { user: 'farux user' });
                document.getElementById('lang-welcome').innerText = cx.lang.get('welcome');
            }
            document.addEventListener('DOMContentLoaded', updateLangDisplay);
        </script>

        <h2>11. Logging (`cx.log`)</h2>
        <p>A unified logging utility for framework messages.</p>
        <button onclick="cx.log('This is a simple log message.');">Log Message</button>
        <button onclick="cx.log('Important data:', { status: 'online', users: 15 });">Log Data</button>

        <h2>12. Built-in Long Polling (`cx-poll`)</h2>
        <p>Simulate real-time content updates from a server.</p>
        <div cx-poll="/api/polling-data" cx-swap="#polling-output" cx-poll-interval="2000"
             style="border: 1px dashed #b3e5fc; padding: 20px; min-height: 80px; margin-top: 20px; background-color: #e0f2f7; border-radius: 8px;">
            <p style="font-weight: bold;">Live Updates:</p>
            <p id="polling-output">Waiting for first update...</p>
        </div>
        <script>
            let pollingUpdateCount = 0;
            window.mockApi = window.mockApi || {};
            // Mock API endpoint for polling (in a real app, this is your backend)
            window.mockApi['/api/polling-data'] = () => {
                pollingUpdateCount++;
                return `Server Update #${pollingUpdateCount} at ${new Date().toLocaleTimeString()}`;
            };
        </script>

        <h2>13. HTML Helpers (`cx.html`)</h2>
        <p>Utilities for safe HTML manipulation.</p>
        <p>Original (unsafe): `<span id="unsafe-output"></span>`</p>
        <p>Escaped (safe): `<span id="safe-output"></span>`</p>
        <script>
            const unsafeContent = '<script>alert("XSS attempt!");</script><strong>Bold Text</strong> & &lt;more&gt;';
            document.getElementById('unsafe-output').innerHTML = unsafeContent; // Render as is
            document.getElementById('safe-output').innerText = cx.html.escape(unsafeContent); // Render escaped
        </script>

        <h2>14. DOM Manipulation (`cx.dom`)</h2>
        <p>Direct control over DOM elements and styling.</p>
        <div id="manipulate-box" style="width: 100px; height: 100px; background-color: #9b59b6; margin: 10px; border-radius: 8px;"></div>
        <button onclick="cx.dom.hide('#manipulate-box');">Hide Box</button>
        <button onclick="cx.dom.show('#manipulate-box');">Show Box</button>
        <button onclick="cx.dom.addClass('#manipulate-box', 'fancy-border');">Add Class</button>
        <button onclick="cx.dom.removeClass('#manipulate-box', 'fancy-border');">Remove Class</button>
        <button onclick="cx.dom.toggleClass('#manipulate-box', 'highlight');">Toggle Highlight</button>
        <button onclick="cx.dom.style('#manipulate-box', 'backgroundColor', '#e67e22');">Change Color</button>
        <script>
            // Add some CSS for the classes
            const style = document.createElement('style');
            style.innerHTML = `
                .fancy-border { border: 3px dashed #f1c40f; }
                .highlight { box-shadow: 0 0 15px rgba(0, 200, 255, 0.7); }
            `;
            document.head.appendChild(style);
        </script>
        <h3>DOM Template Example</h3>
        <div id="template-output" style="border: 1px dashed #bdc3c7; padding: 10px; margin-top: 15px; background-color: #ecf0f1; border-radius: 6px;"></div>
        <template id="my-template">
            <p>Item: <strong>{{name}}</strong> (ID: {{id}})</p>
            <p>Description: {{desc}}</p>
        </template>
        <button onclick="
            const template = cx.dom.get('#my-template');
            const data = { name: 'farux-Item', id: 101, desc: 'A dynamically generated item.' };
            const populated = cx.dom.template(template.content.cloneNode(true), data);
            cx.dom.get('#template-output').innerHTML = ''; // Clear previous
            cx.dom.get('#template-output').appendChild(populated);
        ">Populate Template</button>


        <h2>15. AJAX Direct (`cx.ajax.get`, `cx.ajax.post`)</h2>
        <p>Make direct AJAX calls and handle responses manually.</p>
        <div id="direct-ajax-output" style="border: 1px dashed #dbe9f5; padding: 15px; min-height: 80px; margin-top: 15px; background-color: #f7f9fc; border-radius: 8px;">
            Response: <span id="ajax-response-text">No response yet.</span>
        </div>
        <button onclick="
            cx.ajax.get('/api/simple-data',
                (data) => { cx.dom.get('#ajax-response-text').innerText = 'GET Success: ' + data; },
                (err) => { cx.dom.get('#ajax-response-text').innerText = 'GET Error: ' + err.message; }
            );
        ">Direct GET</button>
        <button onclick="
            cx.ajax.post('/api/submit-data', { item: 'Test Item', value: 123 },
                (data) => { cx.dom.get('#ajax-response-text').innerText = 'POST Success: ' + data; },
                (err) => { cx.dom.get('#ajax-response-text').innerText = 'POST Error: ' + err.message; }
            );
        ">Direct POST</button>


    </div>

    <!-- Mock API Server (for demonstration within this single HTML file) -->
    <script>
        window.addEventListener('click', (event) => {
            const target = event.target;
            const url = target.getAttribute('cx-get') || target.getAttribute('cx-post');

            if (url && url.startsWith('/api/')) {
                event.preventDefault();
                if (url === '/api/dynamic-content') {
                    const newContent = `<h3>Loaded Content</h3><p>This was loaded at ${new Date().toLocaleTimeString()}.</p><p>Powered by farux.js AJAX.</p>`;
                    const targetId = target.getAttribute('cx-swap');
                    const transition = target.getAttribute('cx-transition');
                    const targetElement = cx.dom.get(targetId);
                    if (targetElement) {
                        if (transition && transition.startsWith('fade')) {
                            targetElement.style.opacity = '0';
                            setTimeout(() => {
                                targetElement.innerHTML = newContent;
                                targetElement.style.opacity = '1';
                            }, 500);
                        } else if (transition && transition.startsWith('slide-left')) {
                             targetElement.style.transform = 'translateX(-100%)';
                             setTimeout(() => {
                                targetElement.innerHTML = newContent;
                                targetElement.style.transform = 'translateX(0)';
                            }, 500);
                        } else {
                            targetElement.innerHTML = newContent;
                        }
                    }
                } else if (url === '/api/another-content') {
                    const newContent = `<h3>Another Set of Content</h3><p>This is different content from another endpoint, loaded at ${new Date().toLocaleTimeString()}.</p>`;
                    const targetId = target.getAttribute('cx-swap');
                    const transition = target.getAttribute('cx-transition');
                    const targetElement = cx.dom.get(targetId);
                    if (targetElement) {
                         if (transition && transition.startsWith('fade')) {
                            targetElement.style.opacity = '0';
                            setTimeout(() => {
                                targetElement.innerHTML = newContent;
                                targetElement.style.opacity = '1';
                            }, 500);
                        } else if (transition && transition.startsWith('slide-left')) {
                             targetElement.style.transform = 'translateX(-100%)';
                             setTimeout(() => {
                                targetElement.innerHTML = newContent;
                                targetElement.style.transform = 'translateX(0)';
                            }, 500);
                        } else {
                            targetElement.innerHTML = newContent;
                        }
                    }
                } else if (url.startsWith('/pages/')) {
                    const pageName = url.split('/').pop().replace('.html', '');
                    const content = `<h3>${pageName.charAt(0).toUpperCase() + pageName.slice(1)} Page</h3><p>This is the content for the ${pageName} page.</p><p>Loaded via farux.js routing.</p>`;
                    const view = cx.dom.get('[cx-view]');
                    if (view) {
                        view.innerHTML = content;
                        history.pushState({}, '', url);
                    }
                } else if (url.startsWith('/api/polling-data')) {
                     const targetElement = cx.dom.get('#polling-output');
                     if (targetElement && window.mockApi && window.mockApi['/api/polling-data']) {
                         targetElement.innerText = window.mockApi['/api/polling-data']();
                     }
                } else if (url === '/api/simple-data') {
                    // Simulate cx.ajax.get response
                    cx.ajax.get = (u, s, e) => s(`Hello from Simple Data API at ${new Date().toLocaleTimeString()}`);
                    target.onclick(); // Re-trigger the actual button click handler
                } else if (url === '/api/submit-data') {
                    // Simulate cx.ajax.post response
                     cx.ajax.post = (u, d, s, e) => s(`Data received by API: ${JSON.stringify(d)} at ${new Date().toLocaleTimeString()}`);
                     target.onclick(); // Re-trigger the actual button click handler
                }
            }
        });

        // Replace alert with custom message box
        window.alert = function(message) {
            cx.dom.flash.add('info', message);
        };
    </script>
</body>
</html>
*/