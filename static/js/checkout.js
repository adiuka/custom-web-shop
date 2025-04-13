// This is your test secret API key.
const stripe = Stripe("pk_test_51RAFkcGdxe6jUhJ0pI4QTNPZ9DZxF5V2OKbMQnvCO9b3SkojJRHCanRIUJFn23PDAfgWki4vzNEzDXxECx4N6X3c000au32GRm");

initialize();

// Create a Checkout Session
async function initialize() {
  const fetchClientSecret = async () => {
    const response = await fetch("/create-checkout-session", {
      method: "POST",
    });
    const { clientSecret } = await response.json();
    return clientSecret;
  };

  const checkout = await stripe.initEmbeddedCheckout({
    fetchClientSecret,
  });

  // Mount Checkout
  checkout.mount('#checkout');
}