// Frontend SPA Controller for AI-Based Phishing URL Detection System

document.addEventListener('DOMContentLoaded', () => {
    // Navigation & Views
    const introView = document.getElementById('intro-view');
    const homeView = document.getElementById('home-view');
    const resultView = document.getElementById('result-view');
    
    const btnGetStarted = document.getElementById('btn-get-started');
    const btnCheckAnother = document.getElementById('btn-check-another');
    
    // URL Form & Input Controls
    const urlForm = document.getElementById('url-form');
    const urlInput = document.getElementById('url-input');
    const btnClearUrl = document.getElementById('btn-clear-url');
    const btnAnalyze = document.getElementById('btn-analyze');
    const spinner = btnAnalyze.querySelector('.spinner');
    const btnText = btnAnalyze.querySelector('.btn-text');
    
    // Result Display Elements
    const displayUrl = document.getElementById('display-url');
    const predictionBanner = document.getElementById('prediction-banner');
    const predictionIcon = document.getElementById('prediction-icon');
    const predictionText = document.getElementById('prediction-text');
    const confidenceBarFill = document.getElementById('confidence-bar-fill');
    const confidencePercentage = document.getElementById('confidence-percentage');
    const explanationsList = document.getElementById('explanations-list');

    // 1. Navigation View Switcher
    function switchView(targetView) {
        // Remove active class from all views
        [introView, homeView, resultView].forEach(view => {
            view.classList.remove('active');
        });
        
        // Add active class to target view with a slight timeout to trigger transition
        setTimeout(() => {
            targetView.classList.add('active');
        }, 50);
        
        // Scroll to top of window
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Event Listeners for Navigation
    btnGetStarted.addEventListener('click', () => {
        switchView(homeView);
    });

    btnCheckAnother.addEventListener('click', () => {
        // Reset form inputs and display states
        urlInput.value = '';
        btnClearUrl.classList.add('hidden');
        switchView(homeView);
    });

    // 2. Input Interactive States (Clear Button)
    urlInput.addEventListener('input', () => {
        if (urlInput.value.trim().length > 0) {
            btnClearUrl.classList.remove('hidden');
        } else {
            btnClearUrl.classList.add('hidden');
        }
    });

    btnClearUrl.addEventListener('click', () => {
        urlInput.value = '';
        urlInput.focus();
        btnClearUrl.classList.add('hidden');
    });

    // Helper: Truncate URL nicely for aesthetic presentation
    function truncateUrl(url, maxLength = 60) {
        if (url.length <= maxLength) return url;
        const protocolMatch = url.match(/^(https?:\/\/)/i);
        let clean = url;
        let protocol = '';
        if (protocolMatch) {
            protocol = protocolMatch[1];
            clean = url.slice(protocol.length);
        }
        
        if (clean.length <= maxLength) return url;
        
        const frontLength = Math.ceil((maxLength - 3) / 2);
        const backLength = Math.floor((maxLength - 3) / 2);
        
        return protocol + clean.substring(0, frontLength) + '...' + clean.substring(clean.length - backLength);
    }

    // 3. Submit Handler (AJAX Link Verification)
    urlForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const urlToAnalyze = urlInput.value.trim();
        if (!urlToAnalyze) return;

        // Set Loading State
        btnAnalyze.disabled = true;
        urlInput.disabled = true;
        btnClearUrl.classList.add('hidden');
        spinner.classList.remove('hidden');
        btnText.textContent = 'Analyzing Link...';

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: urlToAnalyze })
            });

            const data = await response.json();

            if (data.success) {
                // Populate Result View Data
                
                // Set Truncated URL Display
                displayUrl.textContent = truncateUrl(data.url, 65);
                displayUrl.href = data.url.match(/^(https?:\/\/)/i) ? data.url : 'http://' + data.url;

                // Reset Status Classes
                predictionBanner.className = 'prediction-banner';
                resultView.className = 'view'; // Reset to default view class

                // Populate Decision Badge & Styling
                if (data.is_phishing) {
                    predictionBanner.classList.add('phishing');
                    resultView.classList.add('phishing');
                    
                    predictionIcon.className = 'fa-solid fa-circle-exclamation';
                    predictionText.textContent = '⚠️ Phishing URL Detected';
                } else {
                    predictionBanner.classList.add('safe');
                    resultView.classList.add('safe');
                    
                    predictionIcon.className = 'fa-solid fa-circle-check';
                    predictionText.textContent = '✅ Safe URL - Legitimate';
                }

                // Confidence Gauge
                confidencePercentage.textContent = `${data.confidence}%`;
                // Animate progress bar fill width (timeout helps make sure DOM is loaded)
                confidenceBarFill.style.width = '0%';
                setTimeout(() => {
                    confidenceBarFill.style.width = `${data.confidence}%`;
                }, 100);

                // Populate Observations List
                explanationsList.innerHTML = '';
                data.explanations.forEach(point => {
                    const li = document.createElement('li');
                    li.textContent = point;
                    explanationsList.appendChild(li);
                });

                // Transition to results page
                switchView(resultView);

            } else {
                alert(`Error: ${data.error || 'Failed to complete analysis.'}`);
            }

        } catch (err) {
            console.error(err);
            alert('An unexpected network error occurred while connecting to the security server.');
        } finally {
            // Restore Active Input States
            btnAnalyze.disabled = false;
            urlInput.disabled = false;
            if (urlInput.value.trim().length > 0) {
                btnClearUrl.classList.remove('hidden');
            }
            spinner.classList.add('hidden');
            btnText.textContent = 'Analyze URL';
        }
    });
});
