console.log("YSummarize content script running on:", window.location.href);

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "ping") {
    sendResponse({ ok: true });
    return; // done
  }

  if (message.action === "generate") {
    // IMPORTANT: immediately acknowledge so popup doesn't show a false error
    sendResponse({ ok: true });

    generateSummary();
    return; // done
  }
});

function generateSummary() {
  const youtubeUrl = window.location.href;
  const apiUrl =
    "http://localhost:5000/api/summarize?youtube_url=" + encodeURIComponent(youtubeUrl);

  const xhr = new XMLHttpRequest();
  xhr.open("GET", apiUrl, true);

  xhr.onload = function () {
    if (xhr.status === 200) {
      try {
        const data = JSON.parse(xhr.responseText);
        chrome.runtime.sendMessage({
          action: "result",
          summary: data.summary || "(Backend returned no summary)"
        });
      } catch {
        chrome.runtime.sendMessage({
          action: "result",
          summary: "Error: Could not parse backend response."
        });
      }
    } else {
      chrome.runtime.sendMessage({
        action: "result",
        summary: "Backend error: HTTP " + xhr.status
      });
    }
  };

  xhr.onerror = function () {
    chrome.runtime.sendMessage({
      action: "result",
      summary: "Network error: backend not reachable (is Flask running?)"
    });
  };

  xhr.send();
}
