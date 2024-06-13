WITH user_message_data AS (
    SELECT
    user_data.*,
    MAX(reg.days_from_registration) as maxdays_reg,
    MAX(act.days_from_last_activity) as maxdays_act

    -- присоединяем даты последних сообщений
    FROM (
        SELECT
        u.*,
        MAX(reg_msgs.time_send) as last_reg_msg_date,
        MAX(act_msgs.time_send) as last_act_msg_date

        FROM main.user u
        -- последнее сообщение по регистрации
        LEFT JOIN
            -- выбираем только записи, относящиеся к регистрации и не позднее введ. даты
            (SELECT * FROM main.list_send_message
                WHERE schedule_id IN
                (SELECT id FROM schedule WHERE days_from_registration NOT NULL)
                AND time_send <= '{0}'
            ) AS reg_msgs
            ON
            u.id = reg_msgs.user_id

        -- последнее сообщение по активности
        LEFT JOIN
            -- выбираем только записи, относящиеся к активности и не позднее введ. даты
            (SELECT * FROM main.list_send_message
                WHERE schedule_id IN
                (SELECT id FROM schedule WHERE days_from_last_activity NOT NULL)
                AND time_send <= '{0}'
            ) AS act_msgs
            ON
            u.id = act_msgs.user_id AND u.last_activity < act_msgs.time_send

        GROUP BY u.id
        ) AS user_data

    -- подбираем кол-во дней для сообщения по регистрации
    LEFT JOIN main.schedule reg
    ON 
    Cast ((julianday('{0}') - julianday(user_data.registration_date)) As Integer) >= reg.days_from_registration
    AND user_data.last_reg_msg_date IS NULL

    -- подбираем кол-во дней для сообщения по активности
    LEFT JOIN main.schedule act
    ON 
    Cast ((julianday('{0}') - julianday(user_data.last_activity)) As Integer) >= act.days_from_last_activity
    AND user_data.last_act_msg_date IS NULL

    GROUP BY user_data.id
)

SELECT
user_message_data.*,
reg_messages.message as reg_msg,
act_messages.message as act_msg

FROM user_message_data

LEFT JOIN main.schedule reg_messages
ON reg_messages.days_from_registration = user_message_data.maxdays_reg

LEFT JOIN main.schedule act_messages
ON act_messages.days_from_last_activity = user_message_data.maxdays_act