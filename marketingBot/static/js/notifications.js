const columnConfigKey = 'marketingbot.notifications.columns';
var _dataTable;

const defaultColumnConfig = {
  bot: true, notification: true,
  type: true, time: true,
};
const columnNames = ['', 'bot', 'notification', 'type', 'time', ''];
var columnConfig = {};

$(function() {
  console.log('[Script][Loaded] API Apps');

  $('.col-show-checkbox').on('change', function(e) {
    storeColumnConfig();
    refreshColumnShow();
  });

  initDataTable();
});


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
              url: "/load-notifications",
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
                  return data.type;
                }
              },
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

function deleteTweetByIdRequest(id) {
  return $.ajax({
    url: `/api/tweets/${id}`,
    method: 'DELETE',
    // data: JSON.stringify(data),
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
  });
}


// Scripts for minority


function refreshTable() {
  _dataTable.api().ajax.reload();
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
  const names = ['bot', 'notification', 'type', 'time'];
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
    if (columnConfig[key] === undefined || config[key] !== columnConfig[key]) {
      setColumnVisibility(index, config[key]);
    }
    $(`#col-show-${key}`).prop('checked', config[key]);
  });
  columnConfig = config;
}
