import React from 'react';
import PropTypes from 'prop-types';


class Likes extends React.Component {
  /* Display number of likes a like/unlike button for one post
   * Reference on forms https://facebook.github.io/react/docs/forms.html
   */
  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = {
      num_likes: 0,
      isToggleOn: 1,
      get_data: false,
    };
    this.handleClick = this.handleClick.bind(this);
  }
  
  componentDidMount() {
    // Call REST API to get number of likes
    fetch(this.props.url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          num_likes: data.likes_count,
          isToggleOn: data.logname_likes_this,
          get_data: true,
        });
      })
      .catch(error => console.log(error)); // eslint-disable-line no-console
  }

  handleClick() {
    if (this.state.isToggleOn) {
      fetch(this.props.url, {
        method: 'DELETE',
        credentials: 'same-origin',
      });
    } else {
      fetch(this.props.url, {
        method: 'POST',
        body: JSON.stringify({}),
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
      });
    }
    if (this.state.isToggleOn) {
      this.setState({
        num_likes: this.state.num_likes - 1,
      });
    } else {
      this.setState({ num_likes: this.state.num_likes + 1 });
    }

    const newToggle = !this.state.isToggleOn;
    this.setState({
      isToggleOn: newToggle,
    });
  }

  render() {
    // Render number of likes
    return (
      <div>
        {this.state && this.state.get_data &&
        <div className="likes">
          <button id="like-unlike-button" onClick={this.handleClick}>
            <p>{this.state.isToggleOn ? 'unlike' : 'like'}</p>
          </button>
          <p>{this.state.num_likes} like{this.state.num_likes !== 1 ? 's' : ''}</p>
        </div>
        }
      </div>
    );
  }
}

Likes.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Likes;
