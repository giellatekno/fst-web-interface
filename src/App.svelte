<script>
  import { t, locale } from "svelte-intl-precompile";
  import { ui_langs } from "./lib/config.js";
  import UILangSelector from "./UILangSelector.svelte";
  import Index from "./Index.svelte";
  import Tools from "./Tools.svelte";

  import {
      ui_lang,
      target_lang,
      selected_tool,
  } from "./lib/stores.js";

  // React to any changes in ui_lang,
  // target_lang, or tool, and update the
  // currenly showing component
  $: current_component = determine_component(
      $ui_lang,
      $target_lang,
      $selected_tool,
  );

  function determine_component(
      ui_lang,
      target_lang,
      tool,
  ) {
      const m = "App.svelte::determine_component()";
      if (!ui_lang) ui_lang = "sme";
      if (!target_lang) {
          console.debug(m + ": show Index");
          return Index;
      } else {
          console.debug(m + ": show Tools");
          return Tools;
      }
  }

  let selecting_language = false;
  let more_languages = false;
  function select_langauge() {
    selecting_language = !selecting_language;
  }

  function show_more_languages() {
    num_langs_shown = langs.length;
  }
</script>

<main>
    <UILangSelector />

    <div>
        <svelte:component
            this={current_component}
        />
    </div>
</main>


<style>
    div {
        margin-left: 34px;
    }
</style>
