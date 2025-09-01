// src/Config.ts  — restore original surface + a couple safe extras
import daisyuiThemes from 'daisyui/theme/object';
import { isNumeric } from './utils/misc';

export const isDev = import.meta.env.MODE === 'development';

// BASE_URL should be the app's origin (not /v1); the code appends /v1 where needed.
export const BASE_URL = new URL('.', document.baseURI).href
  .toString()
  .replace(/\/$/, '');

// === ORIGINAL DEFAULTS (keep types exactly as used across the app) ===
export const CONFIG_DEFAULT = {
  // Do not introduce null/undefined here; components assume concrete types
  apiKey: '',
  systemMessage: '',
  showTokensPerSecond: false,
  showThoughtInProgress: false,
  excludeThoughtOnReq: true,
  pasteLongTextToFileLen: 2500,
  pdfAsImage: false,

  // make sure these default values are in sync with common.h
  samplers: 'edkypmxt', // NOTE: string, not string[]
  temperature: 0.8,
  dynatemp_range: 0.0,
  dynatemp_exponent: 1.0,
  top_k: 40,
  top_p: 0.95,
  min_p: 0.05,
  xtc_probability: 0.0,
  xtc_threshold: 0.1,
  typical_p: 1.0,
  repeat_last_n: 64,
  repeat_penalty: 1.0,
  presence_penalty: 0.0,
  frequency_penalty: 0.0,
  dry_multiplier: 0.0,
  dry_base: 1.75,
  dry_allowed_length: 2,
  dry_penalty_last_n: -1,
  max_tokens: -1,
  custom: '', // JSON string blob for extra params

  // experimental
  pyIntepreterEnabled: false,
} as const;

// Helpful text for settings UI — MUST be plain strings (ReactNode error otherwise)
export const CONFIG_INFO: Record<string, string> = {
  apiKey: 'Set the API Key if you are using --api-key option for the server.',
  systemMessage: 'The starting message that defines how model should behave.',
  pasteLongTextToFileLen:
    'On pasting long text, it will be converted to a file. You can control the file length by setting the value of this parameter. Value 0 means disable.',
  samplers:
    'The order at which samplers are applied, in simplified way. Default is "dkypmxt": dry->top_k->typ_p->top_p->min_p->xtc->temperature',
  temperature:
    'Controls the randomness of the generated text by affecting the probability distribution of the output tokens. Higher = more random, lower = more focused.',
  dynatemp_range:
    'Addon for the temperature sampler. The added value to the range of dynamic temperature, which adjusts probabilities by entropy of tokens.',
  dynatemp_exponent:
    'Addon for the temperature sampler. Smoothes out the probability redistribution based on the most probable token.',
  top_k: 'Keeps only k top tokens.',
  top_p:
    'Limits tokens to those that together have a cumulative probability of at least p',
  min_p:
    'Limits tokens based on the minimum probability for a token to be considered, relative to the probability of the most likely token.',
  xtc_probability:
    'XTC sampler cuts out top tokens; this parameter controls the chance of cutting tokens at all. 0 disables XTC.',
  xtc_threshold:
    'XTC sampler cuts out top tokens; this parameter controls the token probability that is required to cut that token.',
  typical_p:
    'Sorts and limits tokens based on the difference between log-probability and entropy.',
  repeat_last_n: 'Last n tokens to consider for penalizing repetition',
  repeat_penalty:
    'Controls the repetition of token sequences in the generated text',
  presence_penalty:
    'Limits tokens based on whether they appear in the output or not.',
  frequency_penalty:
    'Limits tokens based on how often they appear in the output.',
  dry_multiplier:
    'DRY sampling reduces repetition in generated text even across long contexts. This parameter sets the DRY sampling multiplier.',
  dry_base:
    'DRY sampling reduces repetition in generated text even across long contexts. This parameter sets the DRY sampling base value.',
  dry_allowed_length:
    'DRY sampling reduces repetition in generated text even across long contexts. This parameter sets the allowed length for DRY sampling.',
  dry_penalty_last_n:
    'DRY sampling reduces repetition in generated text even across long contexts. This parameter sets DRY penalty for the last n tokens.',
  max_tokens: 'The maximum number of token per output.',
  custom: '',
};

// Numeric keys list (used elsewhere)
export const CONFIG_NUMERIC_KEYS = Object.entries(CONFIG_DEFAULT)
  .filter((e) => isNumeric(e[1]))
  .map((e) => e[0]);

// Themes (string literals only; keep light/dark first)
export const THEMES = ['light', 'dark'].concat(
  Object.keys(daisyuiThemes).filter((t) => t !== 'light' && t !== 'dark')
);

// A simple app-config type that matches the concrete defaults (no undefined)
export type AppConfig = typeof CONFIG_DEFAULT;

// ——— Extras that some components expect (harmless to include) ———
export const MODELS_ENDPOINT = `${BASE_URL}/v1/models`;
export const CHAT_ENDPOINT = `${BASE_URL}/v1/chat/completions`;

// Keep labels as plain strings in SettingDialog; ensure these are strings, not symbols
export const PENALTY_KEYS: string[] = [
  'presence_penalty',
  'frequency_penalty',
  'repeat_penalty',
];

export default {
  isDev,
  BASE_URL,
  CONFIG_DEFAULT,
  CONFIG_INFO,
  CONFIG_NUMERIC_KEYS,
  THEMES,
  MODELS_ENDPOINT,
  CHAT_ENDPOINT,
  PENALTY_KEYS,
};
