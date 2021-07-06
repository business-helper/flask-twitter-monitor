var _dataTable;

$(function() {
  console.log('[Script][Loaded] API Apps');

  initDataTable();

  $('#add-item').on('click', onClickAddButton);

  $('#website-form').submit(function(e) {
    e.preventDefault();
    if (!confirm('Are you sure to submit?')) return false;
    const formData = {
      name: $('#name').val(),
      consumer_key: $('#consumer_key').val(),
      consumer_secret: $('#consumer_secret').val(),
      access_token: $('#access_token').val(),
      access_token_secret: $('#access_token_secret').val(),
      bearer_token: $('#bearer_token').val(),
      valid: $('#active').is(':checked') ? 1 : 0,
    };

    const id = Number($('#app-id').val());

    const promise = id === -1 ? addApiApp(formData) : updateApiApp(id, formData);
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
              url: "/load-api-apps",
              data: function(extra) {
                  extra.keyword = 'test';
              },
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
                        'false': {'title': 'Inactive', 'class': 'm-badge--warning'},
                        'true': {'title': 'Active', 'class': 'm-badge--success'},
                    };
                    data = data.toString();
                    if (typeof status[data] === 'undefined') {
                        return data;
                    }
                    return '<span class="m-badge ' + status[data].class + ' m-badge--wide">' + status[data].title + '</span>';
                },
              },
              // {
              //     targets: -3,
              //     render: function(data, type, full, meta) {
              //         const url_length = data.length;
              //         if (url_length == 0) {
              //             return `<span class="m-badge m-badge--danger m-badge--wide">Not specified</span>`;
              //         } else {
              //             let display_text = data;
              //             if (url_length > 25) {
              //                 display_text = display_text.substr(0, 25) + '...';
              //             }
              //             return `<a href="${data}" title="${data}" target="_blank">${display_text}</a>`;
              //         }
              //     },
              // },
              {
                  targets: 2,
                  render: function(data, type, full, meta) {
                    const keys = data.split(':');
                    return `
                      <div class="">
                      <p><b>Consumer Key</b>: ${keys[0]}</p>
                      <p><b>Consumer Secret</b>: ${keys[1]}</p>
                      <p><b>Access Token</b>: ${keys[2]}</p>
                      <p><b>Access Token Secret</b>: ${keys[3]}</p>
                      <span style="overflow-wrap: anywhere;"><b>Bearer Token</b>: ${keys[4]}</span>
                      </div>
                    `;
                  },
              },
          ]
      };

      _dataTable.dataTable(settings);
  }
  initTableWithDynamicRows();
}

function updateApiApp(id, data) {
  return $.ajax({
    url: `/api/api-apps/${id}`,
    method: 'put',
    data: JSON.stringify(data),
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
  });
}

function addApiApp(data) {
  return $.ajax({
    url: '/api-app',
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

function getApiAppById(id) {
  return $.ajax({
    url: `/api/api-apps/${id}`,
    method: 'GET',
    // data: JSON.stringify(data),
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
  });
}

function deleteApiAppById(id) {
  return $.ajax({
    url: `/api/api-apps/${id}`,
    method: 'DELETE',
    // data: JSON.stringify(data),
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
  });
}

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
  return getApiAppById(id).then((res) => {
    if (res.status) {
      const { data: app } = res;
      $('#app-id').val(app.id);
      $('#name').val(app.name);
      $('#active').prop('checked', app.valid);
      $('#consumer_key').val(app.consumer_key);
      $('#consumer_secret').val(app.consumer_secret);
      $('#access_token').val(app.access_token);
      $('#access_token_secret').val(app.access_token_secret);
      $('#bearer_token').val(app.bearer_token);

      $('#website-form button[type="submit"]').html('<i class="la la-save"></i>Update');
      $('#form-wrapper').removeClass('_hide').addClass('_show');
    } else {
      toastr.error(res.message);
    }    
  })
  .catch((error) => {
    console.log('[Error]', error);
  })
}

function onDelete(id) {
  if (!confirm('Are you sure proceed to delete?')) return false;
  return deleteApiAppById(id).then((res) => {
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

function emptyForm() {
  $('#website-form').find("input[type=text], input[type=hidden], textarea").val("");
  $('#app-id').val("-1");
  $('#website-form button[type="submit"]').html('<i class="la la-plus"></i>Add');
  $('#form-wrapper').addClass('_hide').removeClass('_show');
}

function refreshTable() {
  _dataTable.api().ajax.reload();
}


