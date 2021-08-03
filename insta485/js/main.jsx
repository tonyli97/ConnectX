import React from 'react';
import ReactDOM from 'react-dom';
import Posts from './posts';


ReactDOM.render(
  <Posts url="/api/v1/p/" />,
  document.getElementById('reactEntry'),
);
