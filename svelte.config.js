import precompileIntl from "svelte-intl-precompile/sveltekit-plugin";

/** @type {import('@sveltejs/kit').Config} */
export default {
  kit: {
    target: '#svelte',
    vite: {
      plugins: [
        // if your translations are defined in /locales/[lang].js
        precompileIntl('intl', "$intl")
        // precompileIntl('locales', '$myprefix') // also you can change import path prefix for json files ($locales by default)
      ]
    }
  }
};
