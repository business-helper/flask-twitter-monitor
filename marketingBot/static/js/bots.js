var _dataTable;

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

      addMetricFilter(app.metrics);

      // botTypeSelected(app.type);
    } else {
      toastr.error(res.message);
    }    
  })
  .catch((error) => {
    console.log('[Error]', error);
  })
}

function onStartBot(id) {
  return startBotByIdRequest(id).then((res) => {
    if (res.status) {
      toastr.success(res.message);
      refreshTable();
    } else {
      toastr.error(res.message);
    }
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

function botTypeSelected(type) {
  // update status of the elements - interval, {star time, end time}
  const isRealTime = type === 'REAL_TIME';
  $('#start_time').attr('disabled', isRealTime);
  $('#end_time').attr('disabled', isRealTime);
  $('#interval').attr('disabled', !isRealTime);
}

function onAddNewFilterWidget(e) {
  if ($('.metric-filter-wrapper').length === 3) {
    toastr.error('You can add max 3 metric filters!');
    return false;
  }
  $('#filters').append(getNewMetricFilterWidget());
}

function onDeleteMetricFilterWidget(e) {
  $(this).closest('.metric-filter-wrapper').remove();
}

function onSelectMetricType(e) {
  const values = [];
  $('.select-metric').each((i, item) => values.push(item.value));
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
              {
                targets: 2,
                render: function (data, type, full, meta) {
                  const status = {
                      'ONE_TIME': {'title': 'One Time', 'class': 'm-badge--info'},
                      'REAL_TIME': {'title': 'Real Time', 'class': 'm-badge--success'},
                  };
                  if (typeof status[data] === 'undefined') {
                      return data;
                  }
                  return '<span class="m-badge ' + status[data].class + ' m-badge--wide">' + status[data].title + '</span>';
              },
              },
              {
                  targets: 3,
                  render: function(data, type, full, meta) {
                    if (data.length) return data.join(',');
                    return `<span class="m-badge m-badge--warning m-badge--wide">No Targets</span>`;
                  },
              },
              {
                  targets: 4,
                  render: function(data, type, full, meta) {
                    if (full[2] === 'REAL_TIME') return data[0];
                    return `${data[1]}-${data[2]}`;
                  },
              },
              {
                targets: 5,
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
            <option vlaue="">- Selct a metric filter type -</option>
            <option value="retweet">Retweet</option>
            <option value="likes">Likes</option>
            <option value="follower">Follower</option>
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
            <option vlaue="">- Selct a metric filter type -</option>
            <option value="retweet" ${key === 'retweet' ? 'selected' : ''}>Retweet</option>
            <option value="likes" ${key === 'likes' ? 'selected' : ''}>Likes</option>
            <option value="follower" ${key === 'follower' ? 'selected' : ''}>Follower</option>
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
