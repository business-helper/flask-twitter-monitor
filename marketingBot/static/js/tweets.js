const columnConfigKey = 'marketingbot.tweets.columns';
var _dataTable;
const defaultColumnConfig = {
  bot: true, target: true,
  text: true, translated: true,
  followers: true, friends: true,
  statuses: true, lists: true,
  retweets: true, likes: true,
  tweeted: true, time: true,
};
const columnNames = ['', 'bot', 'target', 'text', 'translated', 'followers', 'friends', 'statuses', 'lists', 'retweets', 'likes', 'tweeted', 'time', ''];

$(function() {
  console.log('[Script][Loaded] API Apps');

  $('#do-retweet').on('click', function(e) {
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
    })
  });


  $('#do-tweet').on('click', function(e) {
    const tweet_id = $('#tweet-id').val();
    const translated = $('#translated-tweet').val();

    return doTweetById(tweet_id, { translated }).then((res) => {
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
    })
  });


  $('#website-form').submit(function(e) {
    e.preventDefault();
    if (!confirm('Are you sure to submit?')) return false;
    const is_form_valid = validateForm();

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
      const { data: tweet } = res;
      patchTweetModal(tweet);
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

function patchTweetModal(tweet) {
  $('#tweet-id').val(tweet.id);
  $('#origin-tweet').text(tweet.text);
  $('#len-origin').text(tweet.text.length);
  $('#translated-tweet').text(tweet.translated);
  $('#len-translated').text(tweet.translated.length);
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
              url: "/load-tweets",
              data: function(extra) {
                  extra.keyword = 'test';
              },
              type: 'POST',
              dataSrc: 'data'
          },

          columnDefs: [
              {
                  targets: -1,
                  orderable: false,
                  render: function(obj, type, full, meta) {
                    const data = obj.id;
                    const tweet_id = obj.tweet_id;
                    const tweet_link = `https://twitter.com/${full[2]}/status/${tweet_id}`;
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
                targets: -3,
                render: function (data, type, full, meta) {
                  data = data.toString()
                    const status = [
                        {'title': 'None', 'class': 'm-badge--danger'},
                        {'title': 'Retweeted', 'class': 'm-badge--success'},
                        {'title': 'Tweeted', 'class': 'm-badge--info'},
                    ];
                    
                    if (typeof status[data] === 'undefined') {
                        return data;
                    }
                    return '<span class="m-badge ' + status[data].class + ' m-badge--wide">' + status[data].title + '</span>';
                },
              },
              // {
              //   targets: 2,
              //   render: function (data, type, full, meta) {
              //     const status = {
              //         'ONE_TIME': {'title': 'One Time', 'class': 'm-badge--info'},
              //         'REAL_TIME': {'title': 'Real Time', 'class': 'm-badge--success'},
              //     };
              //     if (typeof status[data] === 'undefined') {
              //         return data;
              //     }
              //     return '<span class="m-badge ' + status[data].class + ' m-badge--wide">' + status[data].title + '</span>';
              // },
              // },
              // {
              //     targets: 3,
              //     render: function(data, type, full, meta) {
              //       if (data.length) return data.join(',');
              //       return `<span class="m-badge m-badge--warning m-badge--wide">No Targets</span>`;
              //     },
              // },
              // {
              //     targets: 4,
              //     render: function(data, type, full, meta) {
              //       if (full[2] === 'REAL_TIME') return data[0];
              //       return `${data[1]}-${data[2]}`;
              //     },
              // },
              // {
              //   targets: 5,
              //   render: function(data, type, full, meta) {
              //     if (!data.length) {
              //       return `<span class="m-badge m-badge--danger m-badge--wide">None</span>`
              //     }
              //     const names = data.map((api_key) => api_key.name);
              //     return names.join(',');
              //   },
            // },
          ]
      };

      _dataTable.dataTable(settings);
      refreshColumnShow();
  }
  initTableWithDynamicRows();
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

function doTweetById(id, { translated }) {
  return $.ajax({
    url: `/api/tweets/do-tweet/${id}`,
    method: 'POST',
    data: JSON.stringify({ translated }),
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
  const names = ['bot', 'target', 'text', 'translated', 'followers', 'friends', 'statuses', 'lists', 'retweets', 'likes', 'tweeted', 'time'];
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
    setColumnVisibility(index, config[key]);
    $(`#col-show-${key}`).prop('checked', config[key]);
  });
}
