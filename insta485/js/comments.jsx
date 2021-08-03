import React from 'react';
import PropTypes from 'prop-types';


class Comments extends React.Component {
  /* Display number of likes a like/unlike button for one post
   * Reference on forms https://facebook.github.io/react/docs/forms.html
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = { comments: [], url: '', new_comment: '', updated: false };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
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
          comments: data.comments,
          url: data.url,
          updated: true,
        });
      })
      .catch(error => console.log(error)); // eslint-disable-line no-console
  }

  handleChange(event) {
    this.setState({
      new_comment: event.target.value,
    });
  }

  handleSubmit(event) {
    fetch(this.props.url, {
      method: 'POST',
      body: JSON.stringify({ text: this.state.new_comment }),
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'same-origin',
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        const oneComment = {
          commentid: data.commentid,
          owner: data.owner,
          owner_show_url: data.owner_show_url,
          postid: data.postid,
          text: data.text,
        };
        const preState = this.state.comments;
        preState.push(oneComment);
        this.setState({
          comments: preState,
          new_comment: '',
        });
      });

    event.preventDefault();
  }

  render() {
    // Render number of likes
    const list = this.state.comments.map(comment => (
      <div key={comment.commentid}>
        <a href={comment.owner_show_url}>
          <strong> {comment.owner} </strong>
        </a>
        {comment.text}
      </div>
    ),
    );

    return (
      <div>
        {this.state && this.state.updated &&
          <div>
            <div>
              {list}
            </div>
            <form id="comment-form" onSubmit={this.handleSubmit}>
              <input type="text" value={this.state.new_comment} onChange={this.handleChange} />
              <input type="hidden" value="Submit" />
            </form>
          </div>
        }
      </div>
    );
  }
}

Comments.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Comments;
