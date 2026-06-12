//SPDX-License-Identifier: MIT

pragma solidity ^0.8.19;
error NotRegistrar();
error AlreadyRegistered();
error NotVerified();
error Provoked();
error TLE(); // time limit exceeded
error MLE(); // memory limit exceeded
error MAX_SCORES_INDEX_EXCEEDED();
contract UserRegistrar {
    //EVENTS
    event ScoreUpdate(address indexed user, uint8 role, uint8 score_type, int32 score_delta);


    uint8 public constant MAX_SCORES = 127;
    int32 public max_score;
    int32 public min_score;

    address public registrar;


    struct User {
        bool verified;
        bool provoked;
        bytes32 kyc_hash;
        uint32 identity_steps;
        uint32 auth_steps;
    }
    mapping(address => mapping(uint8 => int32)) public scores;
    uint8[] public scores_size;
    uint8[] public identity_profiles;
    uint8[] public auth_profiles;
    mapping(address => User) public users;

    // For simplicity, we use string as keys for positions, but in a production system, these would likely be enums or constants defined elsewhere.
    mapping(string => uint32) public roles_positions;
    mapping(string => uint32) public auth_steps_positions;
    mapping(string => uint32) public identity_steps_positions;
    mapping(string => uint32) public score_positions;


    constructor(int32 _min_score, int32 _max_score) {
        min_score = _min_score;
        max_score = _max_score;
        registrar=msg.sender;
    }
    modifier only_registrar() {
        if (msg.sender != registrar) revert NotRegistrar();
        _;
    }
    modifier valid_user(address _user) {
        if (!users[_user].verified) revert NotVerified();
        if (users[_user].provoked) revert Provoked();
        _;
    }
    function register_user(address _user, bytes32 key_hash) public only_registrar {
        if (users[_user].verified) revert AlreadyRegistered();
        users[_user].kyc_hash = key_hash;
        users[_user].verified = true;
    }
    function update_score(address _user, uint8 role, uint8 score_type, int8 score_delta) public only_registrar valid_user(_user) {
        int32 prev_score = scores[_user][role];
        int32 new_score = prev_score + score_delta;
        if (new_score > max_score)  new_score = max_score;
        else if (new_score < min_score) new_score = min_score;
        scores[_user][role] = new_score;
        emit ScoreUpdate(_user, role,score_type, new_score-prev_score);
    }

    function update_identity_steps(address _user, uint32 steps) public only_registrar  valid_user(_user) {
        users[_user].identity_steps |= steps;
    }
    function revoke_identity_steps(address _user, uint32 steps) public only_registrar valid_user(_user) {
        users[_user].identity_steps &= ~steps;
    }

    function update_auth_steps(address _user, uint32 steps) public only_registrar valid_user(_user) {
        users[_user].auth_steps |= steps;
    }
    function revoke_auth_steps(address _user, uint32 steps) public only_registrar valid_user(_user) {
        users[_user].auth_steps &= ~steps;
    }
    function get_scores(address _user, uint8 role) public view valid_user(_user) returns (int32) {
        return scores[_user][role];
    }
    function is_identity_profile_compliant(address _user, uint8 profile_type) public view valid_user(_user) returns (bool) {
        if (profile_type >= identity_profiles.length) revert MLE();
        uint32 required_steps = identity_profiles[profile_type];
        return (users[_user].identity_steps&required_steps) == required_steps;
    }

    function is_auth_profile_compliant(address _user, uint8 profile_type) public view valid_user(_user) returns (bool) {
        if (profile_type >= auth_profiles.length) revert MLE();
        uint32 required_steps = auth_profiles[profile_type];
        return (users[_user].auth_steps&required_steps) == required_steps;
    }
}