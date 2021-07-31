
function getLocalDateTime(base_time) {
  try {
    let dt = new Date();
    if (typeof base_time === 'string') {
      dt = new Date(base_time);
    } else if (typeof base_time === 'object') {
      dt = base_time;
    }

    const tzMin = dt.getTimezoneOffset();
    const time = dt.getTime() - tzMin * 60 * 1000;
    return new Date(time);
  } catch (error) {
    return new Date().getTime();
  }
}

function formatTime(dt, format = 'YYYY-mm-dd HH:ii:ss') {
  if (typeof dt === 'string') {
    dt = new Date(dt);
  }
  const Y = dt.getFullYear();
  const m = (dt.getMonth() + 1).toString().padStart(2, '0');
  const d = dt.getDate().toString().padStart(2, '0');

  const hh = dt.getHours().toString().padStart(2, '0');
  const mm = dt.getMinutes().toString().padStart(2, '0');
  const ss = dt.getSeconds().toString().padStart(2, '0');

  return format
    .replace('YYYY', Y)
    .replace('mm', m)
    .replace('dd', d)
    .replace('HH', hh)
    .replace('ii', mm)
    .replace('ss', ss);
}

async function sleep(ms) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      resolve(true);
    }, ms);
  });
}