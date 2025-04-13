# custom-web-shop

A simple custom webshop that uses stripe to take payments. Let me give you a walkthrough:
1. To start with, you need to sign up with stripe: https://docs.stripe.com/
2. Once you have done that, you will need to create products with prices. https://dashboard.stripe.com/test/products?active=true
The reason you need top do this, is to get the stripe price id's you can find when entering the product. These will be used to connect our product DB with the stripe checkout page.
3. Once you have the price id, you can then go to the site. Click register and create the first account. Then login. For now, the admin priviledges are managed based on if the current user has a user_id == 1. This will allow you to create a product. For now it takes links as pictures, name description etc. Most important is stripe price id. Pass the one from your stripe dashboard here.
4. Once you have done that, the product should appear in the site dashboard. You are able to add them to the cart etc.
5. Once the cart is clicked, it will take you to a page where you can see the items in cart in the session. 
6. If you click checkout, it will create a stripe checkout page, showing your items in your cart, and total price. Stripe providees test cards for this, so try it out.
7. It should take you to a confirmation page, and a order history should be added to your account. 

LIMITATIONS:
At the current version, the site is absolutelly not safe or user friendly. The site has no price sorting, no search function, cannot send emails. Many bugs can also be found at the time of posting so it should not be used in production. This is a part of an assignment to create a site that works with stripe checkout.

Future Improvements:
1. To start with, the overall design and tidying up of the project. It is very messy, poorly structured and inefficient. Would really like to refactor a lot of code.
2. I am pretty sure, if an unauthenticated user makes an order currently, the order history functionality will absolutelly break the site. Want to fix this.
3. Email Functionality is neccessary. At the current level, you cannot reset your password or get your confirmations on email at all. Want to integrate emailing functionality to send structured mails to customers.
4. User reworking is needed as well. As of now it is very basic.
5. Order history does not work properly, as you cannot see which items you have bought on the specific entry.
6. Random HTML errors can also be found everywhere for now. 
7. Need to rework product functionality as well. I think I want the pictures to exist locally, so that I can seperate each item and have multiple photos.
8. I think adding stripe price id's is very tedious as well. Want to implement funtionality that maybe does that automatically, or just populates products automatically with stripe.
