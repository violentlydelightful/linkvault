// Create Link Form
document.getElementById('create-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const url = document.getElementById('url-input').value;
    const title = document.getElementById('title-input').value;
    const customCode = document.getElementById('custom-code').value;

    try {
        const response = await fetch('/api/link', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url,
                title: title || null,
                custom_code: customCode || null
            })
        });

        const data = await response.json();

        if (data.success) {
            // Show result
            const resultBox = document.getElementById('result-box');
            const resultUrl = document.getElementById('result-url');
            resultUrl.href = data.link.short_url;
            resultUrl.textContent = data.link.short_url;
            resultBox.style.display = 'block';

            // Clear form
            document.getElementById('url-input').value = '';
            document.getElementById('title-input').value = '';
            document.getElementById('custom-code').value = '';
        } else {
            alert(data.error || 'Failed to create link');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

// Copy Link
function copyLink() {
    const url = document.getElementById('result-url').textContent;
    copyToClipboard(url);
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Visual feedback
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    });
}

// Delete Link
async function deleteLink(linkId) {
    if (!confirm('Are you sure you want to delete this link?')) return;

    try {
        const response = await fetch(`/api/link/${linkId}`, { method: 'DELETE' });
        if (response.ok) {
            window.location.reload();
        } else {
            alert('Failed to delete link');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Toggle Active
async function toggleActive(linkId, active) {
    try {
        const response = await fetch(`/api/link/${linkId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_active: active })
        });

        if (response.ok) {
            window.location.reload();
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}
