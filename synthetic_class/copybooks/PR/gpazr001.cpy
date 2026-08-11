******************************************************************
*  COPYBOOK  : GPAZR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : AZ
******************************************************************
 01  RT-PAZ-RATING.

          03 RT-PAZ-TERRITORY-CODE            PIC X(3).
          03 RT-PAZ-CLASS-CODE                PIC X(4).
          03 RT-PAZ-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PAZ-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PAZ-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PAZ-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PAZ-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PAZ-RATED-PREMIUM             PIC 9(9)V9(2).
