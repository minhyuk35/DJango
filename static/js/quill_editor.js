"use strict";
(() => {
    const mounts = Array.from(document.querySelectorAll("[data-quill]"));
    if (!mounts.length)
        return;
    if (typeof Quill === "undefined")
        return;
    const getCookie = (name) => {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2)
            return parts.pop().split(";").shift() || null;
        return null;
    };
    const uploadImage = async (file) => {
        const form = new FormData();
        form.append("image", file);
        const csrf = getCookie("csrftoken");
        const resp = await fetch("/files/upload-image/", {
            method: "POST",
            headers: csrf ? { "X-CSRFToken": csrf } : undefined,
            body: form,
        });
        if (!resp.ok)
            throw new Error("upload failed");
        const data = (await resp.json());
        if (!data.url)
            throw new Error("no url");
        return data.url;
    };
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
        const toolbar = quill.getModule("toolbar");
        if (toolbar) {
            toolbar.addHandler("image", () => {
                const input = document.createElement("input");
                input.type = "file";
                input.accept = "image/*";
                input.onchange = async () => {
                    var _a;
                    const f = (_a = input.files) === null || _a === void 0 ? void 0 : _a[0];
                    if (!f)
                        return;
                    try {
                        const url = await uploadImage(f);
                        const range = quill.getSelection(true) || { index: quill.getLength(), length: 0 };
                        quill.insertEmbed(range.index, "image", url, "user");
                        quill.setSelection(range.index + 1, 0);
                    }
                    catch (e) {
                        alert("이미지 업로드에 실패했습니다. (관리자 로그인 필요)");
                    }
                };
                input.click();
            });
        }
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
