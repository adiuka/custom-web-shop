initialize();

async function initialize() {
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  const sessionId = urlParams.get('session_id');

  if (!sessionId) {
    console.error("No session_id found in URL.");
    return;
  }

  try {
    const response = await fetch(`/session-status?session_id=${sessionId}`);
    const session = await response.json();

    if (session.status === 'open') {
      window.location.replace('/checkout');
    } else if (session.status === 'complete') {
      document.getElementById('customer-email').textContent = session.customer_email;
    } else {
      console.warn("Unhandled session status:", session.status);
    }
  } catch (error) {
    console.error("Error fetching session status:", error);
  }
}