import { useEffect, useState } from 'react';
import StorageUtils from '../utils/storage';
import { useAppContext } from '../utils/app.context';
import { classNames } from '../utils/misc';
import daisyuiThemes from 'daisyui/theme/object';
import { THEMES, MODELS_ENDPOINT } from '../Config';
import {
  Cog8ToothIcon,
  MoonIcon,
  Bars3Icon,
} from '@heroicons/react/24/outline';

type ApiModel = { name: string; display_name?: string; type?: string };

const SELECTED_MODEL_KEY = 'warriorgpt.selectedModel';

export default function Header() {
  const [selectedTheme, setSelectedTheme] = useState(StorageUtils.getTheme());
  const { setShowSettings } = useAppContext();

  // model state lives here (single place)
  const [models, setModels] = useState<ApiModel[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>(
    localStorage.getItem(SELECTED_MODEL_KEY) || ''
  );

  const setTheme = (theme: string) => {
    StorageUtils.setTheme(theme);
    setSelectedTheme(theme);
  };

  // apply theme to <body>
  useEffect(() => {
    document.body.setAttribute('data-theme', selectedTheme);
    document.body.setAttribute(
      'data-color-scheme',
      daisyuiThemes[selectedTheme]?.['color-scheme'] ?? 'auto'
    );
  }, [selectedTheme]);

  // inside Header.tsx

  // fetch models once
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const resp = await fetch(MODELS_ENDPOINT);
        if (!resp.ok) throw new Error(`Failed to fetch models: ${resp.status}`);
        const raw = await resp.json();

        // Normalize into ApiModel[]
        let arr: ApiModel[] = [];
        if (Array.isArray(raw)) {
          arr = raw;
        } else if (raw && Array.isArray(raw.data)) {
          // OpenAI-style format
          arr = raw.data.map((m: any) => ({
            name: m.id,
            display_name: m.id,
            type: 'openai',
          }));
        } else if (raw && Array.isArray(raw.models)) {
          // our /props-style
          arr = raw.models as ApiModel[];
        } else {
          throw new Error('Unrecognized models payload');
        }

        if (cancelled) return;
        setModels(arr);

        if (!selectedModel && arr.length > 0) {
          const first = arr[0].name;
          setSelectedModel(first);
          localStorage.setItem(SELECTED_MODEL_KEY, first);
          window.dispatchEvent(
            new CustomEvent('warriorgpt:model-changed', { detail: first })
          );
        }
      } catch (err) {
        console.error('Failed to load models in Header', err);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleChangeModel = (name: string) => {
    setSelectedModel(name);
    localStorage.setItem(SELECTED_MODEL_KEY, name);
    // fire a global event so other components can react if needed
    window.dispatchEvent(
      new CustomEvent('warriorgpt:model-changed', { detail: name })
    );
  };

  return (
    <div className="flex flex-row items-center pt-6 pb-6 sticky top-0 z-10 bg-base-100">
      {/* open sidebar button */}
      <label
        htmlFor="toggle-drawer"
        className="btn btn-ghost lg:hidden"
        aria-label="Open sidebar"
      >
        <Bars3Icon className="h-5 w-5" />
      </label>

      {/* App title */}
      <div className="grow text-2xl font-bold ml-2">🪓 WarriorGPT</div>

      {/* Model selector (right side) */}
      <div className="mr-3 hidden sm:flex items-center gap-2">
        <span className="text-sm opacity-70">Model</span>
        <select
          className="select select-sm max-w-xs"
          value={selectedModel}
          onChange={(e) => handleChangeModel(e.target.value)}
          aria-label="Select model"
        >
          {models.map((m) => (
            <option key={m.name} value={m.name}>
              {m.display_name || m.name}
            </option>
          ))}
        </select>
      </div>

      {/* action buttons (top right) */}
      <div className="flex items-center">
        <div
          className="tooltip tooltip-bottom"
          data-tip="Settings"
          onClick={() => setShowSettings(true)}
        >
          <button className="btn" aria-hidden={true}>
            {/* settings button */}
            <Cog8ToothIcon className="w-5 h-5" />
          </button>
        </div>

        {/* theme controller */}
        <div className="tooltip tooltip-bottom" data-tip="Themes">
          <div className="dropdown dropdown-end dropdown-bottom">
            <div
              tabIndex={0}
              role="button"
              className="btn m-1"
              aria-label="Theme"
            >
              <MoonIcon className="w-5 h-5" />
            </div>
            <ul
              tabIndex={0}
              className="dropdown-content bg-base-300 rounded-box z-[1] w-52 p-2 shadow-2xl h-80 overflow-y-auto"
            >
              <li>
                <button
                  className={classNames({
                    'btn btn-sm btn-block btn-ghost justify-start': true,
                    'btn-active': selectedTheme === 'auto',
                  })}
                  onClick={() => setTheme('auto')}
                >
                  auto
                </button>
              </li>
              {THEMES.map((theme) => (
                <li key={theme}>
                  <input
                    type="radio"
                    name="theme-dropdown"
                    className="theme-controller btn btn-sm btn-block btn-ghost justify-start"
                    aria-label={theme}
                    value={theme}
                    checked={selectedTheme === theme}
                    onChange={(e) => e.target.checked && setTheme(theme)}
                  />
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
