import React from 'react';
import PropTypes from 'prop-types';
import Likes from './likes';
import Comments from './comments';
import moment from 'moment'


function onDoubleClick() {
  let isClick = false;
  let clickNum = 0;
  return function ({ singleClick, doubleClick, params }) {
    // 如果没有绑定双击函数，直接执行单击程序
    if (!doubleClick) {
      return singleClick && singleClick(params);
    }
  
    clickNum++;
    // 毫秒内点击过后阻止执行定时器
    if (isClick) {
      return;
    }
    isClick = true;

    setTimeout(() => {
      // 超过1次都属于双击
      if (clickNum > 1) {
        doubleClick && doubleClick(params);
      } else {
        singleClick && singleClick(params);
      }
      clickNum = 0;
      isClick = false;
    }, 300);
  };
}

const onDoubleClickFn = onDoubleClick();


class Post extends React.Component {
  /* Display number of likes a like/unlike button for one post
   * Reference on forms https://facebook.github.io/react/docs/forms.html
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = {
      age: '',
      img_url: '',
      owner: '',
      owner_img_url: '',
      owner_show_url: '',
      post_show_url: '',
      url: '',
      get_data: false,
    };
    this.changelikes = this.changelikes.bind(this);
  }

  componentDidMount() {
    // Call REST API to get number of likes
    //console.log('this.props.url',this.props.url)
    fetch(this.props.url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        var diff = moment(data.age).fromNow();
        this.setState({
          age: diff,
          img_url: data.img_url,
          owner: data.owner,
          owner_img_url: data.owner_img_url,
          owner_show_url: data.owner_show_url,
          post_show_url: data.post_show_url,
          url: data.url,
          get_data: true,
        });
      })
      .catch(error => console.log(error)); // eslint-disable-line no-console
  }

  changelikes () {
    this.Likes.handleClick()
  }

  render() {
    // Render number of likes
    
    return (
      <div>
        {this.state && this.state.get_data &&
        <div className="card border-secdonary w-50 mx-auto">
          <div className="card-header">
            <nav className="navbar">
              <div>
                <a href={this.state.owner_show_url}>
                  <img
                    src={this.state.owner_img_url}
                    width="40"
                    className="d-inline-block align-center"
                    alt=""
                  />
                  <strong> {this.state.owner} </strong>
                </a>
              </div>
              <span className="navbar-text">
                <a href={this.state.post_show_url}>
                  <strong> {this.state.age} </strong>
                </a>
              </span>
            </nav>
          </div>

          
          <img src={this.state.img_url} className="w-100" alt="" 
          onClick={
            () => onDoubleClickFn({
                      singleClick: (e) => {
                      },
                      doubleClick: (e) => {
                        this.changelikes()
                      },
                      params: 123,
                   })
            }
          />
          
          <div className="card-footer bg-transparent">
            <Likes url={`${this.state.url}likes/`} ref={Likes => this.Likes = Likes} />
            <Comments url={`${this.state.url}comments/`} />
          </div>
        </div> }
      </div>
    );
  }
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Post;
