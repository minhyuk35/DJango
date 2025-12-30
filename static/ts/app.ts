(() => {
  const path = window.location.pathname.replace(/\/+$/, "") || "/";
  const links = document.querySelectorAll<HTMLAnchorElement>("a.nav-link");
  links.forEach((link) => {
    const href = (link.getAttribute("href") || "").replace(/\/+$/, "") || "/";
    if (href === path) link.classList.add("active");
  });

  const html = document.documentElement as HTMLElement;
  const button = document.getElementById("theme-toggle") as HTMLButtonElement | null;

  type Theme = "dark" | "light";
  const safeGet = (key: string): string | null => {
    try {
      return window.localStorage.getItem(key);
    } catch {
      return null;
    }
  };

  const safeSet = (key: string, value: string) => {
    try {
      window.localStorage.setItem(key, value);
    } catch {
      // ignore (private mode / blocked storage)
    }
  };

  const getStored = (): Theme | null => {
    const t = safeGet("theme");
    return t === "light" || t === "dark" ? t : null;
  };

  const getDefaultTheme = (): Theme => {
    const prefersLight = window.matchMedia?.("(prefers-color-scheme: light)")?.matches;
    return prefersLight ? "light" : "dark";
  };

  const setTheme = (theme: Theme) => {
    html.dataset.theme = theme;
    safeSet("theme", theme);
    if (button) {
      const icon = button.querySelector("i");
      if (icon) icon.className = theme === "dark" ? "bi bi-sun" : "bi bi-moon-stars";
      button.title = theme === "dark" ? "라이트 테마" : "다크 테마";
    }
  };

  setTheme(getStored() ?? getDefaultTheme());
  button?.addEventListener("click", () => {
    const current = (html.dataset.theme as Theme) || "dark";
    setTheme(current === "dark" ? "light" : "dark");
  });
})();
