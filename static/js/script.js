// Example: simple alert on button click
document.addEventListener('DOMContentLoaded', () => {
  const buttons = document.querySelectorAll('button');
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      console.log('Button clicked!');
    });
  });
});
