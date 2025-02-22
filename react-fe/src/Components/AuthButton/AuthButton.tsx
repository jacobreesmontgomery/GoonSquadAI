import styled from "styled-components";

const StyledButton = styled.a`
    background-color: orange;
    color: black;
    padding: 0.625rem 1.25rem;
    font-size: 1rem;
    border: none;
    cursor: pointer;
    border-radius: 0.3125rem;
    transition: background-color 0.3s ease;
    text-decoration: none;

    &:hover {
        background-color: #e88317; /* Darker shade of orange on hover */
    }
`;

export default function AuthButton() {
    return (
        <StyledButton href="http://localhost:5001/api/new-athlete/strava-auth">
            Authenticate with my app
        </StyledButton>
    );
}
