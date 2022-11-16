<script>
  import LocaleSelector from "./components/LocaleSelector.svelte";
  import LangSelector from "./components/LangSelector.svelte";
  import Index from "./routes/Index.svelte";
  import ToolsIndex from "./routes/ToolsIndex.svelte";
  import AnalyzeWord from "./routes/AnalyzeWord.svelte";
  import Generate from "./routes/Generate.svelte";
  import Spellcheck from "./routes/Spellcheck.svelte";
  import Disambiguate from "./routes/Disambiguate.svelte";
  import Dependency from "./routes/Dependency.svelte";
  import Hyphenation from "./routes/Hyphenation.svelte";
  import Transcription from "./routes/Transcription.svelte";

  import { lang, tool } from "./lib/stores.js";

  // React to any changes in lang or tool,
  // and update the currenly showing component
  $: current_component = determine_component(
      $lang,
      $tool,
  );

    function determine_component(lang, tool) {
        if (!lang) return Index;

        switch (tool) {
            case "":
            default:
                return ToolsIndex;
            case "analyze":
                return AnalyzeWord;
            case "generate":
                return Generate;
            case "disambiguate":
                return Disambiguate;
            case "dependency":
                return Dependency;
            case "hyphenation":
                return Hyphenation;
            case "transcription":
                return Transcription;
            case "spellcheck":
                return Spellcheck;
      }
  }
</script>

<main>
    <header>
        <LocaleSelector />
        <LangSelector />
    </header>

    <div>
        <svelte:component
            this={current_component}
        />
    </div>
</main>


<style>
    header {
        display: flex;
        align-items: center;
        margin-top: 6px;
        margin-left: 6px;
    }
    div {
        margin-left: 34px;
    }
</style>
