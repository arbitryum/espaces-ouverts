(function () {
  "use strict";

  function setRuleState(rule, valid) {
    rule.classList.toggle("text-success", valid);
    rule.classList.toggle("text-error", !valid);
    rule.querySelector("span").textContent = valid ? "✓" : "○";
  }

  function updateValidation() {
    const password = document.getElementById("id_password1");
    const confirmation = document.getElementById("id_password2");
    if (!password || !confirmation) return;

    setRuleState(
      document.querySelector('[data-password-rule="length"]'),
      password.value.length >= 8
    );
    setRuleState(
      document.querySelector('[data-password-rule="numeric"]'),
      password.value.length > 0 && !/^\d+$/.test(password.value)
    );
    setRuleState(
      document.querySelector('[data-password-rule="match"]'),
      password.value.length > 0 && password.value === confirmation.value
    );
  }

  function togglePassword(button) {
    const input = document.getElementById(button.dataset.passwordTarget);
    if (!input) return;

    const isVisible = input.type === "text";
    input.type = isVisible ? "password" : "text";
    button.setAttribute("aria-label", isVisible ? "Afficher le mot de passe" : "Masquer le mot de passe");
    button.setAttribute("title", isVisible ? "Afficher le mot de passe" : "Masquer le mot de passe");
    button.querySelector(".password-visible-icon").classList.toggle("hidden", !isVisible);
    button.querySelector(".password-hidden-icon").classList.toggle("hidden", isVisible);
  }

  document.addEventListener("DOMContentLoaded", function () {
    const password = document.getElementById("id_password1");
    const confirmation = document.getElementById("id_password2");
    if (password && confirmation) {
      password.addEventListener("input", updateValidation);
      confirmation.addEventListener("input", updateValidation);
      updateValidation();
    }

    document.querySelectorAll(".password-toggle").forEach(function (button) {
      button.addEventListener("click", function () {
        togglePassword(button);
      });
    });
  });
})();
