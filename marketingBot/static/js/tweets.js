const columnConfigKey = 'marketingbot.tweets.columns';
var _dataTable;
var columnConfig = {};
const defaultColumnConfig = {
  bot: true, session: true, target: true,
  text: true, translated: true,
  followers: true, friends: true,
  statuses: true, lists: true,
  retweets: true, likes: true,
  rank: true,
  tweeted: true, time: true,
};
const columnNames = ['', 'bot', 'session', 'target', 'text', 'translated', 'followers', 'friends', 'statuses', 'lists', 'retweets', 'likes', 'rank', 'tweeted', 'time', ''];

const filter = {
  bot: 0,
  session: 0,
  keyword: '',
};

$(function() {
  console.log('[Script][Loaded] API Apps');

  $('#do-retweet').on('click', () => actionWrapper(actionRetweet, 'Are you sure proceed to retweet?'));

  $('#do-tweet').on('click', () => actionWrapper(actionTweet, 'Are you sure to proceed to tweet?'));

  $('#do-comment').on('click', () => actionWrapper(actionComment, 'Are you sure to proceed to comment?'));

  $('#do-quote').on('click', () => actionWrapper(actionQuote, 'Are you sure to proceed to quote?'));

  $('#do-save').on('click', () => actionWrapper(actionSave, 'Are you sure to proceed to save?'));

  $('.col-show-checkbox').on('change', function(e) {
    storeColumnConfig();
    refreshColumnShow();
  });

  $('#filter_bot').on('change', async function(e) {
    filter.bot = $(this).val();
    await refreshSessionOfBot();
    filter.session = 0;
    refreshTable();
  });

  $('#filter_session').on('change', function(e) {
    filter.session = $(this).val();
    refreshTable();
  });

  $('#filter_search').on('change keydown', function(e) {
    if (e.which === 13) {
      filter.keyword = $(this).val();
      refreshTable();
    }    
  });

  $('#enable-add-images').on('change', function(e) {
    const enabled = $(this).is(':checked');
    $('#img-file-container').css('display', enabled ? 'block' : 'none');
  });

  $('#add-image').on('click', function(e) {
    const enabled = $('#enable-add-images').is(':checked');
    if (!enabled) return false;
    const elmAdded = document.querySelectorAll('.custom-img-wrapper');
    if (elmAdded && elmAdded.length >= 4) {
      toastr.error('You can add 4 images at max!');
      return;
    }
    $('#img-file-container').append(`
    <div class="my-2 custom-img-wrapper" style="display: flex; align-items: center;">
      <button type="button" class="remove-custom-image btn btn-danger btn-cons mr-2" style="padding: 0.45rem 0.75rem;"><i class="la la-minus"></i></button>
      <input type="file" class="custom-image-file" />
    </div>
    `);
  });

  $('#img-file-container').on('click', '.remove-custom-image', function() {
    $(this).closest('.custom-img-wrapper').remove();
  });

  $('#website-form').submit(function(e) {
    e.preventDefault();
    if (!confirm('Are you sure to submit?')) return false;
    const is_form_valid = validateForm();

    const data = composeFormData();

    const bot_id = Number($('#bot-id').val());
    const promise = bot_id === -1 ? addBotRequest1(data) : updateBotRequest1(bot_id, data);

    return promise
      .then((res) => {
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

  $('#translated-tweet').on('keyup change', function() {
    $('#len-translated').text($(this).val().length);
  });

  $('#open-download-modal').on('click', openDownloadModal);

  $('#do-download').on('click', actionDownloadTweets);

  $('#download-key-all').on('change', function() {
    $('.download-key-checkbox').prop('checked', $(this).is(':checked'));
  });

  $('.download-key-checkbox:not(#download-key-all)').on('change', function() {
    const total = $('.download-key-checkbox:not(#download-key-all)').length;
    let checked = 0;
    $('.download-key-checkbox:not(#download-key-all)').each((i, item) => {
      if ($(item).is(':checked')) checked ++;
    });
    $('#download-key-all').prop('checked', total === checked);
  });

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

  initDataTable();
});

function onEdit(id) {
  return getTweetByIdRequest(id).then((res) => {
    if (res.status) {
      const { data: tweet, embed } = res;
      patchTweetModal(tweet, embed);
      openTweetModal();
    } else {
      toastr.error(res.message, 'Get a Tweet');
    }    
  })
}

function onDelete(id) {
  if (!confirm('Are you sure proceed to delete?')) return false;
  return deleteTweetByIdRequest(id).then((res) => {
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

function validateForm() {
  return true;
}

function composeFormData() {
  const data = new FormData();
  
  data.append('id', $('#bot-id').val())
  data.append('name', $('#name').val());
  data.append('type', $('#type').val());
  data.append('interval', $('#interval').val());
  data.append('api_keys', $('#api_keys').val());
  data.append('start_time', $('#start_time').val());
  data.append('end_time', $('#end_time').val());
  data.append('schedule_interval', $('#schedule_interval').val());
  data.append('schedule_time', Number($('#schedule_time').val()));

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

function patchTweetModal(tweet, embed) {
  $('#tweet-id').val(tweet.id);
  // $('#origin-tweet').val(tweet.text);
  $('#o-tweet-con').html(embed.html)
  $('#len-origin').text(tweet.text.length);
  $('#translated-tweet').val(tweet.translated);
  $('#len-translated').text(tweet.translated.length);
  $('#enable-add-images').prop('checked', false);
  $('#img-file-container').html('');
}

async function refreshSessionOfBot() {
  return loadSessionOfBotRequest(filter.bot)
    .then(res => {
      if (!res.status) throw new Error(res.message);

      const optionHtml = (value, name) => `<option value="${value}">${formatTime(getLocalDateTime(name), 'YYYY-mm-dd HH:ii')}</option>`;
      const innerHtml = res.data
        .map(noti => optionHtml(noti.id, formatTime(noti.created_at)))
        .reduce((html, optHtml) => html += `\n${optHtml}`, '<option value="0">- Select a session -</option>');
      $('#filter_session').html(innerHtml);
    })
    .catch(error => {
      console.log('[refreshSessionSelection] Error: ', error);
    });
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
          searching: false,

          processing: true,

          paginate: true,

          serverSide: true,

          ajax: {
              url: "/load-tweets",
              data: function(extra) {
                  extra.keyword = filter.keyword;
                  extra.bot = filter.bot;
                  extra.session = filter.session;
              },
              type: 'POST',
              dataSrc: 'data'
          },

          columnDefs: [
              {
                targets: -1,
                label: "Actions",
                orderable: false,
                render: function(obj, type, full, meta) {
                  const data = obj.id;
                  const tweet_id = obj.tweet_id;
                  const tweet_link = `https://twitter.com/${full[3]}/status/${tweet_id}`;
                  return `
                  <a class="edit-row m-portlet__nav-link btn m-btn m-btn--hover-brand m-btn--icon m-btn--icon-only m-btn--pill" title="Open Tweet"
                      href="${tweet_link}" target="_blank">
                    <i class="la la-external-link-square"></i>
                  </a>
                  <span class="edit-row m-portlet__nav-link btn m-btn m-btn--hover-brand m-btn--icon m-btn--icon-only m-btn--pill" title="Edit"
                      onclick="onEdit(${data})"
                      data-domain="${data}">
                    <i class="la la-edit"></i>
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
                label: "Time",
                render: function (data, type, full, meta) {
                  return data 
                    ? formatTime(getLocalDateTime(data), 'YYYY-mm-dd HH:ii')
                    :'<span class="m-badge m-badge--warning m-badge--wide">-</span>';
                },
              },
              {
                targets: -3,
                label: "Tweeted",
                render: function (data, type, full, meta) {
                  data = data.toString()
                    const status = [
                        {'title': 'None', 'class': 'm-badge--danger'},
                        {'title': 'Retweeted', 'class': 'm-badge--success'},
                        {'title': 'Tweeted', 'class': 'm-badge--info'},
                        {'title': 'Commentted', 'class': 'm-badge--warning'},
                        {'title': 'Quoted', 'class': 'm-badge--secondary'},
                    ];
                    
                    if (typeof status[data] === 'undefined') {
                        return data;
                    }
                    return '<span class="m-badge ' + status[data].class + ' m-badge--wide">' + status[data].title + '</span>';
                },
              },
              {
                targets: 1,
                label: "Bot",
                render: function (data, type, full, meta) {
                  return data ? data : '<span class="m-badge m-badge--danger m-badge--wide">Deleted Bot</span>';
                },
              },
              {
                targets: 2,
                label: "Session",
                render: function (data, type, full, meta) {
                  return data ? formatTime(getLocalDateTime(data), 'YYYY-mm-dd HH:ii')
                    :'<span class="m-badge m-badge--warning m-badge--wide">No Session</span>';
                },
              },
          ],
      };

      _dataTable.dataTable(settings);
      refreshColumnShow();
  }
  initTableWithDynamicRows();
}

async function actionWrapper(funcAction, confirm_message) {
  if (!confirm(confirm_message || 'Are you sure to proceed?')) {
    return false;
  }
  showModalLoading(true);
  if (typeof funcAction === 'function') {
    await funcAction();
  }
  return showModalLoading(false);
}

function actionSave() {
  const tweet_id = $('#tweet-id').val();
  const translated = $('#translated-tweet').val();

  return updateTranslationById(tweet_id, translated).then(res => {
    if (res.status) {
      toastr.success(res.message, 'Save Transaltion');
      refreshTable();
    } else {
      toastr.error(res.message, 'Tweet');
    }
  })
  .catch(error => {
    console.log('[Tweet]', error);
    toastr.error(error.message, 'Save Translation');
  });
}

function actionTweet() {
  const tweet_id = $('#tweet-id').val();
  const translated = $('#translated-tweet').val();

  return uploadMediaRequest()
    .then((res) => {
      console.log('[Media UPloaded]', res)
      if (!res.status) {
        // toastr.error(res.message, res.title);
        throw new Error(res.message);
      }
      console.log('[Do Tweet By Id]')
      return doTweetById(tweet_id, { translated, media: res.data });
    })
    .then((res) => {
      if (res.status) {
        toastr.success(res.message, 'Tweet');
        refreshTable();
      } else {
        toastr.error(res.message, 'Tweet');
      }
    })
    .catch((error) => {
      console.log('[Tweet]', error);
      toastr.error(error.message, 'Tweet');
    });
}

function actionRetweet() {
  const tweet_id = $('#tweet-id').val();
  return doRetweetById(tweet_id).then((res) => {
    if (res.status) {
      toastr.success(res.message, 'Retweet');
      refreshTable();
    } else {
      toastr.error(res.message, 'Retweet');
    }
  })
  .catch((error) => {
    console.log('[Error while retweeting]', error);
    toastr.error(error.message, 'Retweet');
  });
}

function actionQuote() {
  const tweet_id = $('#tweet-id').val();
  const text = $('#translated-tweet').val();

  return uploadMediaRequest()
    .then(res => {
      if (!res.status) {
        throw new Error(res.message);
      }
      return commentWithQuote(tweet_id, { text, media: res.data });
    })
    .then(res => {
      if (res.status) {
        toastr.success(res.message, 'Quote');
        refreshTable();
      } else {
        toastr.error(res.message, 'Quote');
      }
    })
    .catch(error => {
      console.log('[Comment]', error);
      toastr.error(error.message, 'Quote');
    });
}

function actionComment() {
  const tweet_id = $('#tweet-id').val();
  const comment = $('#translated-tweet').val();

  return uploadMediaRequest()
    .then(res => {
      if (!res.status) {
        throw new Error(res.message);
      }
      return commentToTweet(tweet_id, { comment, media: res.data });
    })
    .then(res => {
      if (res.status) {
        toastr.success(res.message, 'Comment');
        refreshTable();
      } else {
        toastr.error(res.message, 'Comment');
      }
    })
    .catch(error => {
      console.log('[Comment]', error);
      toastr.error(error.message, 'Comment');
    });
}

function actionDownloadTweets() {
  const fields = [];
  $('.download-key-checkbox:not(#download-key-all)').each((i, item) => {
    if ($(item).is(':checked')) {
      fields.push($(item).prop('id').replace('download-key-', ''));
    }
  });
  const downloadFilter = $('input[name="download-option"]:checked').val() === 'filtered' ? filter : {};

  return downloadTweetRequest(downloadFilter, fields)
    .then(res => {
      if (!res.status) {
        throw new Error(res.message);
      }
      return res.file;
    })
    .then(filename => {
      var link=document.createElement('a');
      document.body.appendChild(link);
      link.href = `download/csv/${filename}`;
      link.click();
      toastr.success('Downloading...');
      closeDownloadModal();
    })
    .catch(error => {
      console.log('[DownloadTweet][Error]', error);
      toastr.error(error.message, 'Download Tweets');
    });

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

function getTweetByIdRequest(id) {
  return $.ajax({
    url: `/api/tweets/${id}`,
    method: 'GET',
    // data: JSON.stringify(data),
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
  });
}

function deleteTweetByIdRequest(id) {
  return $.ajax({
    url: `/api/tweets/${id}`,
    method: 'DELETE',
    // data: JSON.stringify(data),
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
  });
}

function doRetweetById(id) {
  return $.ajax({
    url: `/api/tweets/do-retweet/${id}`,
    method: 'POST',
    // data: JSON.stringify(data),
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
  });
}

function doTweetById(id, { translated, media = [] }) {
  return $.ajax({
    url: `/api/tweets/do-tweet/${id}`,
    method: 'POST',
    data: JSON.stringify({ translated, media }),
    contentType: 'application/json, charset=utf-8',
    dataType: 'json',
  });
}

function updateTranslationById(id, translated) {
  return $.ajax({
    url: `/api/tweets/translate/${id}`,
    method: 'PUT',
    data: JSON.stringify({ translated }),
    contentType: 'application/json, charset=utf-8',
    dataType: 'json',
  });
}

function loadSessionOfBotRequest(bot_id) {
  return $.ajax({
    url: `/api/bots/${bot_id}/sessions`,
    method: 'GET',
    contentType: 'application/json, charset=utf-8',
    dataType: 'json',
  });
}

function uploadMediaRequest() {
  const data = new FormData();
  elem_files = document.querySelectorAll('.custom-image-file');
  let index = 0;
  for (let i = 0; i < elem_files.length; i++) {
    const element = elem_files[i];
    const file = $(element).prop('files')[0]
    if (file) {
      data.append(`file${index}`, file);
      index ++;
    }
  }
  // data.append('nFiles', index);
  return $.ajax({
    url : 'api/tweets/upload/media',
    type : 'POST',
    data : data,
    processData: false,  // tell jQuery not to process the data
    contentType: false,  // tell jQuery not to set contentType
  });
}

function commentToTweet(id, data) {
  return $.ajax({ 
    url: `/api/tweets/comment/${id}`,
    method: 'POST',
    data: JSON.stringify(data),
    contentType: 'application/json, charset=utf-8',
    dataType: 'json',
  });
}

function commentWithQuote(id, data) {
  return $.ajax({ 
    url: `/api/tweets/quote/${id}`,
    method: 'POST',
    data: JSON.stringify(data),
    contentType: 'application/json, charset=utf-8',
    dataType: 'json',
  });
}

function downloadTweetRequest(filter, fields) {
  return $.ajax({ 
    url: `/api/tweets/download`,
    method: 'POST',
    data: JSON.stringify({ filter, fields }),
    contentType: 'application/json, charset=utf-8',
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
}

function refreshTable() {
  _dataTable.api().ajax.reload();
}

function openTweetModal() {
  $('#tweetModal').modal({
    backdrop: 'static',
    keyboard: false
  });
}

function openDownloadModal() {
  $('#downloadTweetModal').modal({
    backdrop: 'static',
    keyboard: false
  });
}

function closeDownloadModal() {
  $('#downloadTweetModal').modal('hide');
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
  const names = ['bot', 'session', 'target', 'text', 'translated', 'followers', 'friends', 'statuses', 'lists', 'retweets', 'likes', 'rank', 'tweeted', 'time'];
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
    if (columnConfig[key] === undefined || columnConfig[key] !== config[key]) {
      setColumnVisibility(index, config[key]);
    }
    $(`#col-show-${key}`).prop('checked', config[key]);
  });
  columnConfig = config;
}

function showModalLoading(show = true) {
  try {
    $('#modal-loading')
      .addClass(show ? 'show-loading' : 'hide-loading')
      .removeClass(show ? 'hide-loading' : 'show-loading');
  } catch (error) {
    console.log('[Error while toggle loading...]', error);
  }
}
