"use strict";
(() => {
    const mounts = Array.from(document.querySelectorAll("[data-quill]"));
    if (!mounts.length)
        return;
    if (typeof Quill === "undefined")
        return;
    const SizeStyle = Quill.import("attributors/style/size");
    SizeStyle.whitelist = ["12px", "14px", "16px", "18px", "24px", "32px"];
    Quill.register(SizeStyle, true);
    mounts.forEach((mount) => {
        const toolbarId = mount.dataset.quillToolbar || "editor-toolbar";
        const textareaId = mount.dataset.quillTextarea || "id_content";
        const textarea = document.getElementById(textareaId);
        if (!textarea)
            return;
        const quill = new Quill(mount, {
            theme: "snow",
            modules: {
                toolbar: `#${toolbarId}`,
                history: { delay: 500, maxStack: 100, userOnly: true },
            },
            placeholder: "내용을 입력하세요…",
        });
        const initialHtml = textarea.value || "";
        if (initialHtml.trim())
            quill.root.innerHTML = initialHtml;
        const sync = () => {
            textarea.value = quill.root.innerHTML;
        };
        quill.on("text-change", sync);
        const form = mount.closest("form");
        form === null || form === void 0 ? void 0 : form.addEventListener("submit", sync);
    });
})();

