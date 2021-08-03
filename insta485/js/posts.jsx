import InfiniteScroll from 'react-infinite-scroll-component';
import React from 'react';
import PropTypes from 'prop-types';
import Post from './post';


class Posts extends React.Component {
  /* Display number of likes a like/unlike button for one post
   * Reference on forms https://facebook.github.io/react/docs/forms.html
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = { next: '', results: [], url: '' };
    this.fetchMoreData = this.fetchMoreData.bind(this);
  }
  
  fetchMoreData() {
    fetch(this.state.next, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          next: data.next,
          results: this.state.results.concat(data.results),
          url: data.url,
        });
      })
      .catch(error => console.log(error)); // eslint-disable-line no-console
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
          next: data.next,
          results: data.results,
          url: data.url,
        });
      })
      .catch(error => console.log(error)); // eslint-disable-line no-console
  }
  render() {
    // Render number of likes
    return (
      <InfiniteScroll
        dataLength={this.state.results.length}
        next={this.fetchMoreData}
        hasMore={true}
        loader={<div>Loading...</div>}
        endMessage={
          <p style={{ textAlign: 'center' }}>
            <b>Yay! You have seen it all</b>
          </p>
        }
      >
        
        {this.state.results.map((result,i) => (
          <div key={i} id={result.postid}>
            <Post url={result.url} />
          </div>
        ))}
      </InfiniteScroll>
    );
  }
}

Posts.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Posts;
