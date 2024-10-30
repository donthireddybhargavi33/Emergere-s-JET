const form = document.getElementById('user-form');
const usernameInput = document.getElementById('username');
const emailInput = document.getElementById('email');

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const username = usernameInput.value.trim();
  const email = emailInput.value.trim();

  console.log('Form data:', { username, email });

  if (!username || !email) {
    alert('Please fill in all fields');
    return;
  }

  // Validate username and email using regular expressions
  const usernameRegex = /^[a-zA-Z0-9_]+$/;
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

  if (!usernameRegex.test(username)) {
    alert('Invalid username');
    return;
  }

  if (!emailRegex.test(email)) {
    alert('Invalid email address');
    return;
  }

  // Submit the form
  form.submit();
  console.log('Form submitted successfully!');
});