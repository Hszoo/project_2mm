import React, { useState } from "react";
import styled from "styled-components";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const Container = styled.div`
  position: relative;
  margin: 30px 0;
  max-width: 375px;
  height: 740px;
  background: white;
  border: 1px solid gray;
  margin: 30px auto;

  @media screen and (max-width: 768px) {
    width: 100%;
    padding-left: 1rem;
    padding-right: 1rem;
  }
`;

const Back = styled.button`
  position: relative;
  margin-top: 17px;
  margin-left: 15px;
  background: transparent;
  border: none;
  cursor: pointer;
`;

const SubTitle = styled.div`
  position: relative;
  top: 25px;
  left: 25px;
`;

const InputDetail = styled.input`
  position: relative;
  width: 300px;
  height: 161px;
  left: 22px;
  top: 55px;
  border-radius: 7px;
  border: 1.5px solid #0085ff;
  font-size: 20px;
  padding-left: 15px;

  ::placeholder {
    color: #7c7c7c;
  }
`;

const NextBtn = styled.button`
  position: relative;
  top: 340px;
  left: 16px;
  background: transparent;
  border: none;
  cursor: pointer;
`;

const Signup3_new = () => {
  const navigate = useNavigate();
  const [info, setInfo] = useState("");

  console.log(localStorage.getItem("token"));
  console.log(localStorage.getItem("code"));

  const onSubmit = async () => {
    try {
      const token = localStorage.getItem("token");
      const code = localStorage.getItem("code"); // Make sure you have the correct code here

      const formData = new FormData();
      if (info) {
        formData.append("info", info);
      }

      const response = await axios.patch(
        `http://127.0.0.1:8000/group/${code}/`, // Use the correct URL with the code parameter
        formData,
        {
          headers: {
            Authorization: `Token ${token}`,
            "Content-Type": "multipart/form-data",
          },
        }
      );

      console.log("Data:", response.data);

      navigate("/Signup4_new");
    } catch (error) {
      console.error("Error creating new post:", error);
    }
  };

  const handleInfoChange = (e) => {
    setInfo(e.target.value);
  };

  return (
    <Container>
      <Back>&nbsp;</Back>
      <SubTitle>
        <img
          src={`${process.env.PUBLIC_URL}/images/subtitle_detail.svg`}
          alt="SubTitle"
        />
      </SubTitle>
      <InputDetail
        placeholder="예)가족에 대한 간단한 설명"
        value={info}
        onChange={handleInfoChange}
      />
      <NextBtn onClick={onSubmit}>
        <img src={`${process.env.PUBLIC_URL}/images/nextbtn.svg`} alt="Next" />
      </NextBtn>
    </Container>
  );
};

export default Signup3_new;
