<script>
    import gt_logo from "./assets/giellatekno_logo_official.png";
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
    import Paradigm from "./routes/Paradigm.svelte";
    import Num from "./routes/Num.svelte";

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
            case "paradigm":
                return Paradigm;
            case "num":
                return Num;
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

    <!--
    <footer>
        <img class="gt_logo" src={gt_logo} alt="Giellatekno">
        <p>Giellatekno, UiT Universitet i Tromsø &mdash; Norges Arktiske Universitet</p>
    </footer>
    -->
</main>


<style>
    header {
        /*height: 44px;*/
        display: flex;
        align-items: center;
        margin-top: 6px;
        margin-left: 6px;
    }
    div {
        /*margin-left: 34px;*/
    }

    /*
    footer {
        color: #ffffff;
        padding: 12px 0 12px 34px;
        display: flex;
        flex-direction: column;
        margin-top: 26px;
        background-color: #0a2d3aee;
        background: linear-gradient(to bottom, #fdfdfd, 70%, #0A2D3A);
        border-top: 1px solid #ddd;
    }
    */

    /*
    footer > img.gt_logo {
        height: 46px;
        width: 136px;
        filter: invert(100%) contrast(85%) drop-shadow(2px 2px 3px #222);
    }
    */
</style>
