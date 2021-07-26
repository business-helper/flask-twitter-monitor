var _dataTable;
var columnConfig = {};
const columnConfigKey = 'marketingbot.bots.columns';
const defaultColumnConfig = {
  name: true, type: true,
  targets: true, period: true,
  apps: true, inclusion: true,
  exclusion: true, status: true,
  enable_cutout: true, cutout: true,
};
const columnNames = ['', 'name', 'type', 'targets', 'period', 'apps', 'inclusion', 'exclusion', 'enable_cutout', 'cutout', 'status', ''];
const targetLangs = {};
const defaultLang = 'JA';
const langData = {
  "ab":{
      "name":"Abkhaz",
      "nativeName":"аҧсуа"
  },
  "aa":{
      "name":"Afar",
      "nativeName":"Afaraf"
  },
  "af":{
      "name":"Afrikaans",
      "nativeName":"Afrikaans"
  },
  "ak":{
      "name":"Akan",
      "nativeName":"Akan"
  },
  "sq":{
      "name":"Albanian",
      "nativeName":"Shqip"
  },
  "am":{
      "name":"Amharic",
      "nativeName":"አማርኛ"
  },
  "ar":{
      "name":"Arabic",
      "nativeName":"العربية"
  },
  "an":{
      "name":"Aragonese",
      "nativeName":"Aragonés"
  },
  "hy":{
      "name":"Armenian",
      "nativeName":"Հայերեն"
  },
  "as":{
      "name":"Assamese",
      "nativeName":"অসমীয়া"
  },
  "av":{
      "name":"Avaric",
      "nativeName":"авар мацӀ, магӀарул мацӀ"
  },
  "ae":{
      "name":"Avestan",
      "nativeName":"avesta"
  },
  "ay":{
      "name":"Aymara",
      "nativeName":"aymar aru"
  },
  "az":{
      "name":"Azerbaijani",
      "nativeName":"azərbaycan dili"
  },
  "bm":{
      "name":"Bambara",
      "nativeName":"bamanankan"
  },
  "ba":{
      "name":"Bashkir",
      "nativeName":"башҡорт теле"
  },
  "eu":{
      "name":"Basque",
      "nativeName":"euskara, euskera"
  },
  "be":{
      "name":"Belarusian",
      "nativeName":"Беларуская"
  },
  "bn":{
      "name":"Bengali",
      "nativeName":"বাংলা"
  },
  "bh":{
      "name":"Bihari",
      "nativeName":"भोजपुरी"
  },
  "bi":{
      "name":"Bislama",
      "nativeName":"Bislama"
  },
  "bs":{
      "name":"Bosnian",
      "nativeName":"bosanski jezik"
  },
  "br":{
      "name":"Breton",
      "nativeName":"brezhoneg"
  },
  "bg":{
      "name":"Bulgarian",
      "nativeName":"български език"
  },
  "my":{
      "name":"Burmese",
      "nativeName":"ဗမာစာ"
  },
  "ca":{
      "name":"Catalan; Valencian",
      "nativeName":"Català"
  },
  "ch":{
      "name":"Chamorro",
      "nativeName":"Chamoru"
  },
  "ce":{
      "name":"Chechen",
      "nativeName":"нохчийн мотт"
  },
  "ny":{
      "name":"Chichewa; Chewa; Nyanja",
      "nativeName":"chiCheŵa, chinyanja"
  },
  "zh":{
      "name":"Chinese",
      "nativeName":"中文 (Zhōngwén), 汉语, 漢語"
  },
  "cv":{
      "name":"Chuvash",
      "nativeName":"чӑваш чӗлхи"
  },
  "kw":{
      "name":"Cornish",
      "nativeName":"Kernewek"
  },
  "co":{
      "name":"Corsican",
      "nativeName":"corsu, lingua corsa"
  },
  "cr":{
      "name":"Cree",
      "nativeName":"ᓀᐦᐃᔭᐍᐏᐣ"
  },
  "hr":{
      "name":"Croatian",
      "nativeName":"hrvatski"
  },
  "cs":{
      "name":"Czech",
      "nativeName":"česky, čeština"
  },
  "da":{
      "name":"Danish",
      "nativeName":"dansk"
  },
  "dv":{
      "name":"Divehi; Dhivehi; Maldivian;",
      "nativeName":"ދިވެހި"
  },
  "nl":{
      "name":"Dutch",
      "nativeName":"Nederlands, Vlaams"
  },
  "en":{
      "name":"English",
      "nativeName":"English"
  },
  "eo":{
      "name":"Esperanto",
      "nativeName":"Esperanto"
  },
  "et":{
      "name":"Estonian",
      "nativeName":"eesti, eesti keel"
  },
  "ee":{
      "name":"Ewe",
      "nativeName":"Eʋegbe"
  },
  "fo":{
      "name":"Faroese",
      "nativeName":"føroyskt"
  },
  "fj":{
      "name":"Fijian",
      "nativeName":"vosa Vakaviti"
  },
  "fi":{
      "name":"Finnish",
      "nativeName":"suomi, suomen kieli"
  },
  "fr":{
      "name":"French",
      "nativeName":"français, langue française"
  },
  "ff":{
      "name":"Fula; Fulah; Pulaar; Pular",
      "nativeName":"Fulfulde, Pulaar, Pular"
  },
  "gl":{
      "name":"Galician",
      "nativeName":"Galego"
  },
  "ka":{
      "name":"Georgian",
      "nativeName":"ქართული"
  },
  "de":{
      "name":"German",
      "nativeName":"Deutsch"
  },
  "el":{
      "name":"Greek, Modern",
      "nativeName":"Ελληνικά"
  },
  "gn":{
      "name":"Guaraní",
      "nativeName":"Avañeẽ"
  },
  "gu":{
      "name":"Gujarati",
      "nativeName":"ગુજરાતી"
  },
  "ht":{
      "name":"Haitian; Haitian Creole",
      "nativeName":"Kreyòl ayisyen"
  },
  "ha":{
      "name":"Hausa",
      "nativeName":"Hausa, هَوُسَ"
  },
  "he":{
      "name":"Hebrew (modern)",
      "nativeName":"עברית"
  },
  "hz":{
      "name":"Herero",
      "nativeName":"Otjiherero"
  },
  "hi":{
      "name":"Hindi",
      "nativeName":"हिन्दी, हिंदी"
  },
  "ho":{
      "name":"Hiri Motu",
      "nativeName":"Hiri Motu"
  },
  "hu":{
      "name":"Hungarian",
      "nativeName":"Magyar"
  },
  "ia":{
      "name":"Interlingua",
      "nativeName":"Interlingua"
  },
  "id":{
      "name":"Indonesian",
      "nativeName":"Bahasa Indonesia"
  },
  "ie":{
      "name":"Interlingue",
      "nativeName":"Originally called Occidental; then Interlingue after WWII"
  },
  "ga":{
      "name":"Irish",
      "nativeName":"Gaeilge"
  },
  "ig":{
      "name":"Igbo",
      "nativeName":"Asụsụ Igbo"
  },
  "ik":{
      "name":"Inupiaq",
      "nativeName":"Iñupiaq, Iñupiatun"
  },
  "io":{
      "name":"Ido",
      "nativeName":"Ido"
  },
  "is":{
      "name":"Icelandic",
      "nativeName":"Íslenska"
  },
  "it":{
      "name":"Italian",
      "nativeName":"Italiano"
  },
  "iu":{
      "name":"Inuktitut",
      "nativeName":"ᐃᓄᒃᑎᑐᑦ"
  },
  "ja":{
      "name":"Japanese",
      "nativeName":"日本語 (にほんご／にっぽんご)"
  },
  "jv":{
      "name":"Javanese",
      "nativeName":"basa Jawa"
  },
  "kl":{
      "name":"Kalaallisut, Greenlandic",
      "nativeName":"kalaallisut, kalaallit oqaasii"
  },
  "kn":{
      "name":"Kannada",
      "nativeName":"ಕನ್ನಡ"
  },
  "kr":{
      "name":"Kanuri",
      "nativeName":"Kanuri"
  },
  "ks":{
      "name":"Kashmiri",
      "nativeName":"कश्मीरी, كشميري‎"
  },
  "kk":{
      "name":"Kazakh",
      "nativeName":"Қазақ тілі"
  },
  "km":{
      "name":"Khmer",
      "nativeName":"ភាសាខ្មែរ"
  },
  "ki":{
      "name":"Kikuyu, Gikuyu",
      "nativeName":"Gĩkũyũ"
  },
  "rw":{
      "name":"Kinyarwanda",
      "nativeName":"Ikinyarwanda"
  },
  "ky":{
      "name":"Kirghiz, Kyrgyz",
      "nativeName":"кыргыз тили"
  },
  "kv":{
      "name":"Komi",
      "nativeName":"коми кыв"
  },
  "kg":{
      "name":"Kongo",
      "nativeName":"KiKongo"
  },
  "ko":{
      "name":"Korean",
      "nativeName":"한국어 (韓國語), 조선말 (朝鮮語)"
  },
  "ku":{
      "name":"Kurdish",
      "nativeName":"Kurdî, كوردی‎"
  },
  "kj":{
      "name":"Kwanyama, Kuanyama",
      "nativeName":"Kuanyama"
  },
  "la":{
      "name":"Latin",
      "nativeName":"latine, lingua latina"
  },
  "lb":{
      "name":"Luxembourgish, Letzeburgesch",
      "nativeName":"Lëtzebuergesch"
  },
  "lg":{
      "name":"Luganda",
      "nativeName":"Luganda"
  },
  "li":{
      "name":"Limburgish, Limburgan, Limburger",
      "nativeName":"Limburgs"
  },
  "ln":{
      "name":"Lingala",
      "nativeName":"Lingála"
  },
  "lo":{
      "name":"Lao",
      "nativeName":"ພາສາລາວ"
  },
  "lt":{
      "name":"Lithuanian",
      "nativeName":"lietuvių kalba"
  },
  "lu":{
      "name":"Luba-Katanga",
      "nativeName":""
  },
  "lv":{
      "name":"Latvian",
      "nativeName":"latviešu valoda"
  },
  "gv":{
      "name":"Manx",
      "nativeName":"Gaelg, Gailck"
  },
  "mk":{
      "name":"Macedonian",
      "nativeName":"македонски јазик"
  },
  "mg":{
      "name":"Malagasy",
      "nativeName":"Malagasy fiteny"
  },
  "ms":{
      "name":"Malay",
      "nativeName":"bahasa Melayu, بهاس ملايو‎"
  },
  "ml":{
      "name":"Malayalam",
      "nativeName":"മലയാളം"
  },
  "mt":{
      "name":"Maltese",
      "nativeName":"Malti"
  },
  "mi":{
      "name":"Māori",
      "nativeName":"te reo Māori"
  },
  "mr":{
      "name":"Marathi (Marāṭhī)",
      "nativeName":"मराठी"
  },
  "mh":{
      "name":"Marshallese",
      "nativeName":"Kajin M̧ajeļ"
  },
  "mn":{
      "name":"Mongolian",
      "nativeName":"монгол"
  },
  "na":{
      "name":"Nauru",
      "nativeName":"Ekakairũ Naoero"
  },
  "nv":{
      "name":"Navajo, Navaho",
      "nativeName":"Diné bizaad, Dinékʼehǰí"
  },
  "nb":{
      "name":"Norwegian Bokmål",
      "nativeName":"Norsk bokmål"
  },
  "nd":{
      "name":"North Ndebele",
      "nativeName":"isiNdebele"
  },
  "ne":{
      "name":"Nepali",
      "nativeName":"नेपाली"
  },
  "ng":{
      "name":"Ndonga",
      "nativeName":"Owambo"
  },
  "nn":{
      "name":"Norwegian Nynorsk",
      "nativeName":"Norsk nynorsk"
  },
  "no":{
      "name":"Norwegian",
      "nativeName":"Norsk"
  },
  "ii":{
      "name":"Nuosu",
      "nativeName":"ꆈꌠ꒿ Nuosuhxop"
  },
  "nr":{
      "name":"South Ndebele",
      "nativeName":"isiNdebele"
  },
  "oc":{
      "name":"Occitan",
      "nativeName":"Occitan"
  },
  "oj":{
      "name":"Ojibwe, Ojibwa",
      "nativeName":"ᐊᓂᔑᓈᐯᒧᐎᓐ"
  },
  "cu":{
      "name":"Old Church Slavonic, Church Slavic, Church Slavonic, Old Bulgarian, Old Slavonic",
      "nativeName":"ѩзыкъ словѣньскъ"
  },
  "om":{
      "name":"Oromo",
      "nativeName":"Afaan Oromoo"
  },
  "or":{
      "name":"Oriya",
      "nativeName":"ଓଡ଼ିଆ"
  },
  "os":{
      "name":"Ossetian, Ossetic",
      "nativeName":"ирон æвзаг"
  },
  "pa":{
      "name":"Panjabi, Punjabi",
      "nativeName":"ਪੰਜਾਬੀ, پنجابی‎"
  },
  "pi":{
      "name":"Pāli",
      "nativeName":"पाऴि"
  },
  "fa":{
      "name":"Persian",
      "nativeName":"فارسی"
  },
  "pl":{
      "name":"Polish",
      "nativeName":"polski"
  },
  "ps":{
      "name":"Pashto, Pushto",
      "nativeName":"پښتو"
  },
  "pt":{
      "name":"Portuguese",
      "nativeName":"Português"
  },
  "qu":{
      "name":"Quechua",
      "nativeName":"Runa Simi, Kichwa"
  },
  "rm":{
      "name":"Romansh",
      "nativeName":"rumantsch grischun"
  },
  "rn":{
      "name":"Kirundi",
      "nativeName":"kiRundi"
  },
  "ro":{
      "name":"Romanian, Moldavian, Moldovan",
      "nativeName":"română"
  },
  "ru":{
      "name":"Russian",
      "nativeName":"русский язык"
  },
  "sa":{
      "name":"Sanskrit (Saṁskṛta)",
      "nativeName":"संस्कृतम्"
  },
  "sc":{
      "name":"Sardinian",
      "nativeName":"sardu"
  },
  "sd":{
      "name":"Sindhi",
      "nativeName":"सिन्धी, سنڌي، سندھی‎"
  },
  "se":{
      "name":"Northern Sami",
      "nativeName":"Davvisámegiella"
  },
  "sm":{
      "name":"Samoan",
      "nativeName":"gagana faa Samoa"
  },
  "sg":{
      "name":"Sango",
      "nativeName":"yângâ tî sängö"
  },
  "sr":{
      "name":"Serbian",
      "nativeName":"српски језик"
  },
  "gd":{
      "name":"Scottish Gaelic; Gaelic",
      "nativeName":"Gàidhlig"
  },
  "sn":{
      "name":"Shona",
      "nativeName":"chiShona"
  },
  "si":{
      "name":"Sinhala, Sinhalese",
      "nativeName":"සිංහල"
  },
  "sk":{
      "name":"Slovak",
      "nativeName":"slovenčina"
  },
  "sl":{
      "name":"Slovene",
      "nativeName":"slovenščina"
  },
  "so":{
      "name":"Somali",
      "nativeName":"Soomaaliga, af Soomaali"
  },
  "st":{
      "name":"Southern Sotho",
      "nativeName":"Sesotho"
  },
  "es":{
      "name":"Spanish; Castilian",
      "nativeName":"español, castellano"
  },
  "su":{
      "name":"Sundanese",
      "nativeName":"Basa Sunda"
  },
  "sw":{
      "name":"Swahili",
      "nativeName":"Kiswahili"
  },
  "ss":{
      "name":"Swati",
      "nativeName":"SiSwati"
  },
  "sv":{
      "name":"Swedish",
      "nativeName":"svenska"
  },
  "ta":{
      "name":"Tamil",
      "nativeName":"தமிழ்"
  },
  "te":{
      "name":"Telugu",
      "nativeName":"తెలుగు"
  },
  "tg":{
      "name":"Tajik",
      "nativeName":"тоҷикӣ, toğikī, تاجیکی‎"
  },
  "th":{
      "name":"Thai",
      "nativeName":"ไทย"
  },
  "ti":{
      "name":"Tigrinya",
      "nativeName":"ትግርኛ"
  },
  "bo":{
      "name":"Tibetan Standard, Tibetan, Central",
      "nativeName":"བོད་ཡིག"
  },
  "tk":{
      "name":"Turkmen",
      "nativeName":"Türkmen, Түркмен"
  },
  "tl":{
      "name":"Tagalog",
      "nativeName":"Wikang Tagalog, ᜏᜒᜃᜅ᜔ ᜆᜄᜎᜓᜄ᜔"
  },
  "tn":{
      "name":"Tswana",
      "nativeName":"Setswana"
  },
  "to":{
      "name":"Tonga (Tonga Islands)",
      "nativeName":"faka Tonga"
  },
  "tr":{
      "name":"Turkish",
      "nativeName":"Türkçe"
  },
  "ts":{
      "name":"Tsonga",
      "nativeName":"Xitsonga"
  },
  "tt":{
      "name":"Tatar",
      "nativeName":"татарча, tatarça, تاتارچا‎"
  },
  "tw":{
      "name":"Twi",
      "nativeName":"Twi"
  },
  "ty":{
      "name":"Tahitian",
      "nativeName":"Reo Tahiti"
  },
  "ug":{
      "name":"Uighur, Uyghur",
      "nativeName":"Uyƣurqə, ئۇيغۇرچە‎"
  },
  "uk":{
      "name":"Ukrainian",
      "nativeName":"українська"
  },
  "ur":{
      "name":"Urdu",
      "nativeName":"اردو"
  },
  "uz":{
      "name":"Uzbek",
      "nativeName":"zbek, Ўзбек, أۇزبېك‎"
  },
  "ve":{
      "name":"Venda",
      "nativeName":"Tshivenḓa"
  },
  "vi":{
      "name":"Vietnamese",
      "nativeName":"Tiếng Việt"
  },
  "vo":{
      "name":"Volapük",
      "nativeName":"Volapük"
  },
  "wa":{
      "name":"Walloon",
      "nativeName":"Walon"
  },
  "cy":{
      "name":"Welsh",
      "nativeName":"Cymraeg"
  },
  "wo":{
      "name":"Wolof",
      "nativeName":"Wollof"
  },
  "fy":{
      "name":"Western Frisian",
      "nativeName":"Frysk"
  },
  "xh":{
      "name":"Xhosa",
      "nativeName":"isiXhosa"
  },
  "yi":{
      "name":"Yiddish",
      "nativeName":"ייִדיש"
  },
  "yo":{
      "name":"Yoruba",
      "nativeName":"Yorùbá"
  },
  "za":{
      "name":"Zhuang, Chuang",
      "nativeName":"Saɯ cueŋƅ, Saw cuengh"
  }
}

$(function() {
  console.log('[Script][Loaded] API Apps');

  initDataTable();

  botTypeSelected('REAL_TIME');

  $(".select2").select2({
    placeholder: "Select here"
  });

  // change event of bot type
  $('#type').on('change', function(e) {
    const type = $(this).val();
    botTypeSelected(type);
  });

  // event to add new metric filter widget.
  $('#add-new-filter-widget').on('click', onAddNewFilterWidget);

  // event to delete metric filter widget
  $('#website-form').on('click', '.btn-remove-filter', onDeleteMetricFilterWidget);

  // select a metric type
  $('#website-form').on('change', '.select-metric', onSelectMetricType)

  // date time picker for start & end time.
  $('.datetime-picker').datetimepicker({})

  // button to toggle item form.
  $('#add-item').on('click', onClickAddButton);

  $('#targets').on('blur', renderTargetTranslationLangs);

  $('#enable-translation').on('change', renderTargetTranslationLangs);

  $('#website-form').submit(function(e) {
    e.preventDefault();
    const is_form_valid = validateForm();

    if (!is_form_valid) {
      return false;
    }

    if (!confirm('Are you sure to submit?')) return false;
    const data = composeFormData();

    const bot_id = Number($('#bot-id').val());
    const promise = bot_id === -1 ? addBotRequest1(data) : updateBotRequest1(bot_id, data);

    return promise.then((res) => {
      if (res.status) {
        toastr.success(res.message);
        refreshTable();
        emptyForm();
      } else {
        toastr.error(res.message);
      }
    })
    .catch((error) => {
      console.log('[Error]', error);
      toastr.error(error.message);
    });
  });

  $('.col-show-checkbox').on('change', function(e) {
    storeColumnConfig();
    refreshColumnShow();
  });

  $('.rank-checkbox').on('change', onRankFactorUpdated);

  // deprecated.
  // submit action in the item form.
  $('#website-form1').submit(function(e) {
    e.preventDefault();
    if (!confirm('Are you sure to submit?')) return false;
    const formData = {
      name: $('#name').val(),
      targets: $('#targets').val().split(',').filter((it) => !!it.trim()),
      api_keys: $('#api_keys').val(),
      inclusion_keywords: $('#inclusion_keywords').val().split(',').filter(it => it.trim()),
      exclusion_keywords: $('#exclusion_keywords').val().split(',').filter(it => it.trim()),
      interval: $('#interval').val(),
    };

    const id = Number($('#bot-id').val());

    console.log('[Testing values]', id, formData);

    const promise = id === -1 ? addBotRequest(formData) : updateBotRequest(id, formData);
    return promise.then((res) => {
      if (res.status) {
        toastr.success(res.message);
        refreshTable();
        emptyForm();
      } else {
        toastr.error(res.message);
      }
    })
    .catch((error) => {
      console.log('[Error]', error);
      toastr.error(error.message);
    })
  });
});

function onClickAddButton() {
  const isEditing = Number($('#app-id').val()) > -1;
  const opened = $('#form-wrapper').hasClass('_show');
  emptyForm();
  if (opened && !isEditing) {
    $('#form-wrapper').addClass('_hide').removeClass('_show');
  } else {
    $('#form-wrapper').removeClass('_hide').addClass('_show');
  }
}

function onEdit(id) {
  return getApiAppByIdRequest(id).then((res) => {
    if (res.status) {
      const { data: app } = res;
      $('#bot-id').val(app.id);
      $('#name').val(app.name);
      $('#targets').val(app.targets.join(','));
      $('#api_keys').val(app.api_keys).trigger('change');
      $('#inclusion_keywords').val(app.inclusion_keywords.join(','));
      $('#exclusion_keywords').val(app.exclusion_keywords.join(','));
      $('#interval').val(app.period);

      $('#website-form button[type="submit"]').html('<i class="la la-save"></i>Update');
      $('#form-wrapper').removeClass('_hide').addClass('_show');
      $('#type').val(app.type);
      $('#start_time').val(app.start_time);
      $('#end_time').val(app.end_time);
      $('#schedule_interval').val(app.schedule_interval);
      $('#schedule_time').val(app.schedule_time);
      $('#enable-translation').prop('checked', app.enable_translation);
      $('#translator').val(app.translator);

      addMetricFilter(app.metrics);

      botTypeSelected(app.type);

      configureRankFactors(app.rank_factors);
      renderTargetTranslationLangs(app.target_langs);
    } else {
      toastr.error(res.message);
    }    
  })
  .catch((error) => {
    console.log('[Error]', error);
  })
}

function onStartBot(id) {
  // startBotByIdRequest(id)
  return startBotByIdRequest(id).then((res) => {
    // if (res.status) {
      // toastr.success('A bot has been started!');
      // refreshTable();
    // } else {
    //   toastr.error(res.message);
    // }
  })
  .catch((error) => {
    console.log('[Task][Start]', id, error);
    toastr.error(error.message);
  });
}

function onStopBot(id) {
  return stopBotByIdRequest(id).then((res) => {
    if (res.status) {
      toastr.success(res.message);
      refreshTable();
    } else {
      toastr.error(res.message);
    }
  })
  .catch((error) => {
    console.log('[Task][Stop]', id, error);
    toastr.error(error.message);
  })
}

function onDelete(id) {
  if (!confirm('Are you sure proceed to delete?')) return false;
  return deleteApiAppByIdRequest(id).then((res) => {
    if (res.status) {
      toastr.success(res.message);
      refreshTable();
    } else {
      toastr.error(res.message);
    }
  })
  .catch((error) => {
    console.log('[Delete]', error);
    toastr.error(error.message);
  })
}

/// --------------- Scripts for UI Operation Events

function renderTargetTranslationLangs(target_langs = {}) {
  const translation_enabled = $('#enable-translation').is(':checked');
  const targets = getTargetsAsArray();
  const selectElements = targets.map(target => composeSelectElement(target, target_langs[target])).join('\n');
  $('#translation-langs').html(selectElements);
  $('.target-lang-item select').prop('disabled', !translation_enabled);
  $('#translator').prop('disabled', !translation_enabled);
}

function onRankFactorUpdated(e) {
  const { numerators, denominators } = getRankFactors();
  
  const sel_numerators = Object.keys(numerators).filter(key => numerators[key]).map(it => it.charAt(0).toUpperCase() + it.substr(1, it.length - 1));
  const sel_denominators = Object.keys(denominators).filter(key => denominators[key]).map(it => it.charAt(0).toUpperCase() + it.substr(1, it.length - 1));

  let str_formula = '';
  if (sel_numerators.length === 0 && sel_denominators.length === 0) {
    str_formula = 'Please define the rank formula, or it will be zero!';
  } else if (sel_denominators.length === 0) {
    str_formula = sel_numerators.join(' + ');
  } else if (sel_numerators.length === 0) {
    str_formula = `1 / ${sel_denominators.length > 1 ? `( ${sel_denominators.join(' + ')} )`  : sel_denominators[0]}`;
  } else {
    const num = sel_numerators.length === 1 ? sel_numerators[0] : `( ${sel_numerators.join(' + ')} )`;
    const denom = sel_denominators.length === 1 ? sel_denominators[0] : `( ${sel_denominators(' + ')} )`;
    str_formula = `${num} / ${denom}`;
  }

  $('#rank-formula').text(str_formula);
}

function configureRankFactors(factors) {
  Object.keys(factors).forEach(key => {
    $(`#rank-${key}`).prop('checked', factors[key]);
  });
  onRankFactorUpdated();
}

function botTypeSelected(type) {
  // update status of the elements - interval, {star time, end time}
  const isRealTime = type === 'REAL_TIME';
  $('#start_time').attr('disabled', isRealTime);
  $('#end_time').attr('disabled', isRealTime);
  $('#schedule_interval').attr('disabled', isRealTime);
  $('#schedule_time').attr('disabled', isRealTime);
  $('#interval').attr('disabled', !isRealTime);
}

function onAddNewFilterWidget(e) {
  if ($('.metric-filter-wrapper').length === 5) {
    toastr.error('You can add 6 metric filters at max!');
    return false;
  }
  $('#filters').append(getNewMetricFilterWidget());
}

function onDeleteMetricFilterWidget(e) {
  $(this).closest('.metric-filter-wrapper').remove();
}

function onSelectMetricType(e) {
  let values = [];
  $('.select-metric').each((i, item) => values.push(item.value));
  values = values.filter((value) => !!value);
  const unique_values = values.filter((value, i, self) => self.indexOf(value) === i);
  if (values.length > unique_values.length) {
    toastr.warning('You must select different filter types!', 'Metric Filter');
  }
}

function addMetricFilter(metrics) {
  $('#filters').html('');
  Object.keys(metrics).forEach((key, index) => {
    $('#filters').append(getMetricFilterWidget(key, metrics[key]));
  });
}

function validateForm() {
  let valid = true;
  
  const type = $('#type').val();
  if (type === 'REAL_TIME') {
    const interval = $('#interval').val();
    if (!interval || Number(interval) <= 0) {
      toastr.error('The field is required or must be greater than 0.', 'Interval');
      valid = false;
    }
  } else if (type === 'ONE_TIME') {
    const start_time = $('#start_time').val();
    const end_time = $('#end_time').val();
    const schedule_interval = $("#schedule_interval").val();
    const schedule_time = $('#schedule_time').val();
    if (!start_time) {
      toastr.error('The field is required!', 'Start Time');
      valid = false;
    }
    if (!end_time) {
      toastr.error('The field is required!', 'End Time');
      valid = false;
    }
    if (!schedule_interval && Number(schedule_interval) < 0) {
      toastr.error('The field must not be smaller than 0', 'Schedule Interval');
      valid = false;
    }
    // if (!schedule_time) {
    //   toastr.error('The field is required!', 'Schedule Time');
    //   valid = false;
    // }
  }
  return valid;
}

function composeFormData() {
  const data = new FormData();
  const { rank_factors } = getRankFactors();
  data.append('id', $('#bot-id').val())
  data.append('name', $('#name').val());
  data.append('type', $('#type').val());
  data.append('interval', $('#interval').val());
  data.append('api_keys', $('#api_keys').val());
  data.append('start_time', $('#start_time').val());
  data.append('end_time', $('#end_time').val());
  data.append('schedule_interval', $('#schedule_interval').val());
  data.append('schedule_time', $('#schedule_time').val());
  data.append('enable_translation', $('#enable-translation').is(':checked'));
  data.append('target_langs', JSON.stringify(getTargetLangs()));
  data.append('translator', $('#translator').val());
  data.append('rank_factors', JSON.stringify(rank_factors));
  data.append('enable_cutout', $('#enable_cutout').is(':checked'));
  data.append('cutout', $('#cutout').val());

  const metricKeys = [];
  const metricValues = [];
  const metrics = {};
  $('.select-metric').each((i, item) => metricKeys.push(item.value));
  $('.min-metric').each((i, item) => metricValues.push(item.value));
  metricKeys.forEach((key, i) => {
    metrics[metricKeys[i]] = metricValues[i];
  });
  data.append('metrics', JSON.stringify(metrics));

  const ids = ['targets', 'inclusion_keywords', 'exclusion_keywords'];
  ids.forEach((id, i) => {
    data.append(id, $(`#${id}_file`).prop('files')[0] || $(`#${id}`).val());
  })

  return data;
}


// ------------------- Scripts for API requests

function initDataTable() {
  // Initialize datatable with ability to add rows dynamically
  var initTableWithDynamicRows = function() {
      _dataTable = $('#tableWithDynamicRows');

      var settings = {
          responsive: true,
          //== DOM Layout settings
          // dom: `<'row'<'col-sm-12'tr>>
          // <'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7 dataTables_pager'lp>>`,

          lengthMenu: [5, 10, 25, 50],

          pageLength: 10,

          language: {
              'lengthMenu': 'Display _MENU_',
          },
          order: [
              [ 0, "asc" ]
          ],
          searching: true,

          processing: true,

          paginate: true,

          serverSide: true,

          ajax: {
              url: "/load-bots",
              data: function(extra) {
                  extra.keyword = 'test';
              },
              type: 'POST',
              dataSrc: 'data'
          },

          columnDefs: [
              {
                  targets: -1,
                  label: 'Actions',
                  orderable: false,
                  render: function(data, type, full, meta) {
                    return `
                    <span class="edit-row m-portlet__nav-link btn m-btn m-btn--hover-brand m-btn--icon m-btn--icon-only m-btn--pill" title="Edit"
                        onclick="onEdit(${data})"
                        data-domain="${data}">
                      <i class="la la-edit"></i>
                    </span>
                    <span href="#" class="delete-row m-portlet__nav-link btn m-btn m-btn--hover-brand m-btn--icon m-btn--icon-only m-btn--pill" title="Start"
                      onclick="onStartBot(${data})"
                      data-domain="${data}">
                      <i class="la la-play"></i>
                    </span>
                    <span href="#" class="delete-row m-portlet__nav-link btn m-btn m-btn--hover-brand m-btn--icon m-btn--icon-only m-btn--pill" title="Stop"
                      onclick="onStopBot(${data})"
                      data-domain="${data}">
                      <i class="la la-stop"></i>
                    </span>
                    <span href="#" class="delete-row m-portlet__nav-link btn m-btn m-btn--hover-brand m-btn--icon m-btn--icon-only m-btn--pill" title="Remove"
                      onclick="onDelete(${data})"
                      data-domain="${data}">
                      <i class="la la-trash"></i>
                    </span>`;
                  },
              },
              {
                targets: -2,
                label: 'Status',
                render: function (data, type, full, meta) {
                    const status = {
                        'IDLE': {'title': 'Idle', 'class': 'm-badge--info'},
                        'RUNNING': {'title': 'Running', 'class': 'm-badge--success'},
                    };
                    data = data.toString();
                    if (typeof status[data] === 'undefined') {
                        return data;
                    }
                    return '<span class="m-badge ' + status[data].class + ' m-badge--wide">' + status[data].title + '</span>';
                },
              },
              // {
              //   targets: -3,
              //   orderable: false,
              //   render: function(data) {
              //     return data;
              //   }
              // },
              {
                targets: -4,
                label: 'Enable Cutout',
                orderable: false,
                render: function(data) {
                  data = data.toString();
                  const status = {
                    'false': {'title': 'Disabled', 'class': 'm-badge--danger'},
                    'true': {'title': 'Enabled', 'class': 'm-badge--success'},
                };
                if (typeof status[data] === 'undefined') {
                    return data;
                }
                return '<span class="m-badge ' + status[data].class + ' m-badge--wide">' + status[data].title + '</span>';
                }
              },
              {
                targets: 2,
                label: 'Type',
                render: function (data, type, full, meta) {
                  const status = {
                      'ONE_TIME': {'title': 'One Time', 'class': 'm-badge--info'},
                      'REAL_TIME': {'title': 'Real Time', 'class': 'm-badge--success'},
                  };
                  if (typeof status[data] === 'undefined') {
                      return data;
                  }
                  const next_run_time = full[full.length - 1];
                  const next_run_element = !next_run_time ? '' : 
                  `<div class="mt-1">
                      <span class="m-badge m-badge--primary m-badge--wide" style="white-space: nowrap;">
                        <i class="flaticon-calendar-with-a-clock-time-tools mr-1"></i>
                        ${next_run_time.replace("+09:00", "JST")}
                      </span>
                    </div>`;
                  
                  return `
                  <div style="display: flex; flex-direction: column;">
                    <div class="text-center">
                      <span class="m-badge ${status[data].class} m-badge--wide">${status[data].title}</span>
                    </div>
                    ${next_run_element}
                  </div>
                  `;
              },
              },
              {
                  targets: 3,
                  label: 'Targets',
                  render: function(data, type, full, meta) {
                    if (data.length) return data.join(', ');
                    return `<span class="m-badge m-badge--warning m-badge--wide">No Targets</span>`;
                  },
              },
              {
                  targets: 4,
                  label: 'Period',
                  orderable: false,
                  render: function(data, type, full, meta) {
                    if (full[2] === 'REAL_TIME') return data[0];
                    return `${data[1]}-${data[2]}`;
                  },
              },
              {
                targets: 5,
                label: 'API Apps',
                orderable: false,
                render: function(data, type, full, meta) {
                  if (!data.length) {
                    return `<span class="m-badge m-badge--danger m-badge--wide">None</span>`
                  }
                  const names = data.map((api_key) => api_key.name);
                  return names.join(',');
                },
            },
          ]
      };

      _dataTable.dataTable(settings);
  }
  initTableWithDynamicRows();
  refreshColumnShow();
}

function updateBotRequest(id, data) {
  return $.ajax({
    url: `/api/bots/${id}`,
    method: 'put',
    data: JSON.stringify(data),
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
  });
}

function updateBotRequest1(id, data) {
  return $.ajax({
    url : `/api/bot_form/${id}`,
    type : 'PUT',
    data : data,
    processData: false,  // tell jQuery not to process the data
    contentType: false,  // tell jQuery not to set contentType
  });
}

function addBotRequest(data) {
  return $.ajax({
    url: '/api/bots',
    method: 'POST',
    data: JSON.stringify(data),
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
  });
  // return $.ajax({
  //   url: url,
  //   method: 'post',
  //   data: JSON.stringify(data),
  //   contentType: "application/json; charset=utf-8",
  //   dataType: "json"
  // });
}

function addBotRequest1(data) {
  return $.ajax({
    url : 'api/bot_form',
    type : 'POST',
    data : data,
    processData: false,  // tell jQuery not to process the data
    contentType: false,  // tell jQuery not to set contentType
  });
}

function startBotByIdRequest(id) {
  return $.ajax({
    url: `/tasks/${id}/start`,
    method: 'POST',
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
  });
}

function stopBotByIdRequest(id) {
  return $.ajax({
    url: `/tasks/${id}/stop`,
    method: 'POST',
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
  });
}

function getApiAppByIdRequest(id) {
  return $.ajax({
    url: `/api/bots/${id}`,
    method: 'GET',
    // data: JSON.stringify(data),
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
  });
}

function deleteApiAppByIdRequest(id) {
  return $.ajax({
    url: `/api/bots/${id}`,
    method: 'DELETE',
    // data: JSON.stringify(data),
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
  });
}

// Scripts for minority

function emptyForm() {
  $('#website-form').find("input[type=text], input[type=hidden], textarea").val("");
  $('#bot-id').val("-1");
  $('#website-form button[type="submit"]').html('<i class="la la-plus"></i>Add');
  $('#form-wrapper').addClass('_hide').removeClass('_show');
  $('#filters').html('');
  onRankFactorUpdated();
  $('#enable-translation').prop('checked', false);
  $('.rank-checkbox').prop('checked', false);

  // translation langs
  $('#translation-langs').html('');
  $('#translator').prop('disabled', true);
  // $('.target-lang-item select').prop('disabled', !translation_enabled);
}

function refreshTable() {
  _dataTable.api().ajax.reload();
}

function getNewMetricFilterWidget() {
  return `
  <div class="metric-filter-wrapper row">
    <div class="col-sm-12 col-md-6">
      <div class="form-group form-group-default">
        <label>Metric Type<span class="text-danger">*</span></label>
        <div style="display: flex; align-items: center;">
          <div style="width: 80px;">
            <button type="button" style="margin-right: 10px;" class="btn-remove-filter btn btn-danger m-btn m-btn--custom m-btn--icon m-btn--air" title="Remove this filter"
              ><i class="la la-minus"></i>
            </button>
          </div>
          <select class="form-control select-metric" required>
            <option value="">- Selct a metric filter type -</option>
            <optgroup label="User">
              <option value="follower">Followers</option>
              <option value="friend">Friends</option>
              <option value="tweets">Total Tweets</option>
              <option value="lists">Lists</option>
            </optgroup>
            <optgroup label="Tweet">
              <option value="retweet">Retweets</option>
              <option value="likes">Likes</option>
            </optgroup>
          </select>
        </div>
      </div>
    </div>
    <div class="col-sm-12 col-md-6">
        <div class="form-group form-group-default">
            <label>Min Number<span class="text-danger">*</span></label>
            <input class="form-control min-metric" type="number" placeholder="50" required />
        </div>
    </div>
  <div>
  `;
}

function getMetricFilterWidget(key, value) {
  return `
  <div class="metric-filter-wrapper row">
    <div class="col-sm-12 col-md-6">
      <div class="form-group form-group-default">
        <label>Metric Type<span class="text-danger">*</span></label>
        <div style="display: flex; align-items: center;">
          <div style="width: 80px;">
            <button type="button" style="margin-right: 10px;" class="btn-remove-filter btn btn-danger m-btn m-btn--custom m-btn--icon m-btn--air" title="Remove this filter"
              ><i class="la la-minus"></i>
            </button>
          </div>
          <select class="form-control select-metric" required>
            <option value="">- Selct a metric filter type -</option>
            <optgroup label="User">
              <option value="follower" ${key === 'follower' ? 'selected' : ''}>Followers</option>
              <option value="friend" ${key === 'friend' ? 'selected' : ''}>Friends</option>
              <option value="tweets" ${key === 'tweets' ? 'selected' : ''}>Total Tweets</option>
              <option value="lists" ${key === 'lists' ? 'selected' : ''}>Lists</option>
            </optgroup>
            <optgroup label="Tweet">
              <option value="retweet" ${key === 'retweet' ? 'selected' : ''}>Retweets</option>
              <option value="likes" ${key === 'likes' ? 'selected' : ''}>Likes</option>
            </optgroup>
          </select>
        </div>
      </div>
    </div>
    <div class="col-sm-12 col-md-6">
        <div class="form-group form-group-default">
            <label>Min Number<span class="text-danger">*</span></label>
            <input class="form-control min-metric" type="number" value="${value}" placeholder="50" required />
        </div>
    </div>
  <div>
  `;
}

async function sleep(ms) {
  return new Promise((resolve) => {
    resolve(true);
  }, ms);
}

function setColumnVisibility(index, show) {
  _dataTable.fnSetColumnVis(index, show);
}

function loadColumnConfig() {
  try {
    const strConfig = window.localStorage.getItem(columnConfigKey);
    if (!strConfig) return defaultColumnConfig;
    return JSON.parse(strConfig);
  } catch (e) {
    return defaultColumnConfig;
  }
}

function storeColumnConfig() {
  const names = Object.keys(defaultColumnConfig);
  const config = {};
  names.forEach((name) => {
    config[name] = $(`#col-show-${name}`).is(':checked');
  });
  window.localStorage.setItem(columnConfigKey, JSON.stringify(config));
}

function refreshColumnShow() {
  const config = loadColumnConfig();
  Object.keys(config).forEach((key) => {
    const index = columnNames.indexOf(key);
    if (columnConfig[key] === undefined || config[key] !== columnConfig[key])
    setColumnVisibility(index, config[key]);
    $(`#col-show-${key}`).prop('checked', config[key]);
  });
  columnConfig = config;
}

function getRankFactors() {
  const numerators = {
    retweets: true,
    likes: true,
    comments: true,
  };
  const denominators = { followers: true };
  
  Object.keys(numerators).forEach((key) => {
    numerators[key] = $(`#rank-${key}`).is(':checked');
  });
  Object.keys(denominators).forEach((key) => {
    denominators[key] = $(`#rank-${key}`).is(':checked');
  });
  return { numerators, denominators, rank_factors: { ...numerators, ...denominators } };
}

function getTargetsAsArray() {
  const str_targets = $('#targets').val();
  return targets = str_targets.split('\n')
    .reduce((_t, line) => _t = _t.concat(line.split(',')), [])
    .map(t => t.trim())
    .filter(t =>  !!t.trim());
}

function composeSelectElement(target, lang) {
  lang = lang || defaultLang;
  return `
  <div class="col-sm-12 col-md-6 target-lang-item" style="align-items: center;">
    <label>${target}</label>
    <select class="form-control" data-target="${target}">
      <option value="NONE">Don't translate!</option>
      ${
        Object.keys(langData)
          .map(key => `<option value="${key.toUpperCase()}" ${key === lang.toLowerCase() ? 'selected' : ''}>${langData[key].name}</option>`)
          .join('\n')
      }
    </select>
  </div>
  `;
}

function getTargetLangs() {
  const targetLangs = {};
  $('.target-lang-item > select').each((i, item) => targetLangs[item.getAttribute('data-target')] = item.value);
  return targetLangs;
}
